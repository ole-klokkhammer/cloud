#!/usr/bin/env python3
"""detector - RTSP YOLO11 object detector (python/torch, CUDA).

    camera -> mediamtx substream -> per-frame YOLO11 (torch CUDA; the torch
    wheel bundles its own CUDA runtime, so only the driver is needed from
    the host) -> per-burst BEST-FRAME selection (conf x target-area score)
    -> one JPEG still per burst + one NATS event per burst

stills are the source of truth (the embedder polls the dir); the NATS event
is deduped signal for consumers. config: env vars, see detector.env.example.
"""
import asyncio
import json
import os
import signal
import threading
import time
from collections import deque
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

import cv2
import nats
import torch
from ultralytics import YOLO


# ---------------------------------------------------------------- config

def _env(name, default):
    return os.environ.get(name, default)

def _env_int(name, default):
    return int(_env(name, default))

def _env_float(name, default):
    return float(_env(name, default))

def _env_ints(name, default):
    raw = _env(name, default)
    return [int(x) for x in raw.split(",") if x.strip()] or [int(x) for x in default.split(",")]

CFG = dict(
    rtsp_url=_env("DETECTOR_RTSP_URL", "rtsp://mediamtx.homelan:8554/entrance_roof_sub"),
    model=_env("DETECTOR_MODEL", "/models/yolo11m.pt"),
    classes=_env_ints("DETECTOR_CLASS", "15"),
    frame_width=_env_int("DETECTOR_FRAME_WIDTH", 1280),
    input_size=_env_int("DETECTOR_INPUT_SIZE", 640),
    min_conf=_env_float("DETECTOR_MIN_CONF", 0.5),
    max_fps=_env_float("DETECTOR_MAX_FPS", 10),
    burst_window=_env_float("DETECTOR_BURST_WINDOW_SECS", 2.0),
    event_dir=_env("DETECTOR_EVENT_DIR", "/detections/events"),
    camera=_env("DETECTOR_CAMERA", "entrance_roof"),
    device=_env("DETECTOR_DEVICE", "cuda"),
    nats_url=_env("NATS_URL", "nats://nats.homelan:4222"),
    nats_subject=_env("NATS_SUBJECT", "surveillance.detector"),
)


def log(msg):
    print(f"[detector] {msg}", flush=True)

def log_event(obj):
    print(f"[detector] {json.dumps(obj, separators=(',', ':'))}", flush=True)


# ---------------------------------------------------------------- nats publisher

class NatsPub(threading.Thread):
    """background publisher: auto-reconnect; drops nothing, stills never wait on NATS."""

    def __init__(self, url, subject):
        super().__init__(daemon=True, name="nats")
        self.url, self.subject = url, subject
        self._q = asyncio.Queue()
        self._stop = False

    def stop(self):
        self._stop = True

    def publish(self, payload):
        self._q.put_nowait(json.dumps(payload, separators=(",", ":")).encode())

    def run(self):
        asyncio.run(self._run())

    async def _run(self):
        while not self._stop:
            try:
                nc = await nats.connect([self.url], name="detector")
                log(f"nats connected: {self.url}")
                while not self._stop:
                    raw = await self._q.get()
                    await nc.publish(self.subject, raw)
                await nc.close()
                return
            except Exception as e:
                if self._stop:
                    return
                log(f"nats disconnected ({e}); retry in 5s - stills keep flowing")
                await asyncio.sleep(5)


# ---------------------------------------------------------------- burst state

@dataclass
class Candidate:
    score: float            # conf x target-area fraction
    frame: object           # full-res BGR ndarray (for the still)
    ts: datetime
    conf: float
    label: str
    box: tuple              # xyxy in full-res frame coords


# ---------------------------------------------------------------- main

def main():
    stop = threading.Event()
    signal.signal(signal.SIGTERM, lambda *a: stop.set())
    signal.signal(signal.SIGINT, lambda *a: stop.set())

    log(f"watching {CFG['rtsp_url']} (classes: {','.join(map(str, CFG['classes']))})")

    device = CFG["device"]
    if device == "cuda" and not torch.cuda.is_available():
        log("cuda requested but unavailable - running on CPU")
        device = "cpu"
    model = YOLO(CFG["model"])
    try:
        model.to(device)
        log(f"device: {device} (torch {torch.__version__}, cuda {torch.version.cuda})")
    except Exception as e:
        device = "cpu"
        model.to("cpu")
        log(f"cuda init failed ({e}) - running on CPU")
    # warm the CUDA context so the first real frame isn't a 10s spike
    model.predict(torch.zeros(1, 3, CFG["input_size"], CFG["input_size"], device=device),
                  verbose=False)
    log(f"model ready: {CFG['model']} (input {CFG['input_size']}x{CFG['input_size']})")

    nats_pub = NatsPub(CFG["nats_url"], CFG["nats_subject"])
    nats_pub.start()

    def open_capture():
        cap = cv2.VideoCapture(CFG["rtsp_url"], cv2.CAP_FFMPEG)
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)   # low latency: never process old frames
        return cap

    cap = open_capture()
    stream_ok = False
    ring: deque = deque(maxlen=16)
    last_det = None
    last_infer = 0.0
    last_hb = time.monotonic()
    last_dets = 0
    frames = 0
    t0 = time.monotonic()
    min_interval = 1.0 / CFG["max_fps"]

    def store_still(cand):
        """best frame -> JPEG at <= frame_width wide; returns (path, box-in-still)."""
        img = cand.frame
        fh, fw = img.shape[:2]
        scale = min(1.0, CFG["frame_width"] / fw)
        if scale < 1.0:
            img = cv2.resize(img, (int(fw * scale), int(fh * scale)), interpolation=cv2.INTER_AREA)
        p = Path(CFG["event_dir"]) / f"{cand.label}_{cand.ts.strftime('%Y%m%d_%H%M%S')}.jpg"
        p.parent.mkdir(parents=True, exist_ok=True)
        cv2.imwrite(str(p), img, [int(cv2.IMWRITE_JPEG_QUALITY), 90])
        return p, [round(v * scale) for v in cand.box]

    while not stop:
        ret, frame = cap.read()
        if not ret or frame is None:
            time.sleep(5.0 if not stream_ok else 0.5)
            cap.release()
            cap = open_capture()
            stream_ok = False
            log("stream lost - restarting capture")
            continue

        fh, fw = frame.shape[:2]
        if not stream_ok:
            stream_ok = True
            log(f"stream {fw}x{fh} (stills <= {CFG['frame_width']}px wide)")
            log(f"capture started ({fw}x{fh} bgr frames)")

        frames += 1
        now = time.monotonic()
        if now - last_infer < min_interval:
            time.sleep(0.05)      # throttle: next read hands over a newer frame
            continue
        last_infer = now

        res = model.predict(frame, imgsz=CFG["input_size"], conf=CFG["min_conf"],
                            iou=0.45, classes=CFG["classes"], verbose=False)[0]
        dets = []
        if res.boxes is not None and len(res.boxes):
            xyxy = res.boxes.xyxy.cpu().numpy()
            confs = res.boxes.conf.cpu().numpy()
            clss = res.boxes.cls.cpu().numpy().astype(int)
            names = model.names
            for (x1, y1, x2, y2), c, cl in zip(xyxy, confs, clss):
                if int(cl) in CFG["classes"] and c >= CFG["min_conf"]:
                    dets.append((float(c), str(names.get(int(cl), cl)),
                                 (float(x1), float(y1), float(x2), float(y2))))

        if dets:
            last_dets = len(dets)
            best = max(dets, key=lambda d: d[0])
            last_det = now
            log_event({"event": "detection", "camera": CFG["camera"],
                       "ts": datetime.now(timezone.utc).isoformat(),
                       "dets": len(dets), "best_conf": round(best[0], 3),
                       "bbox": [round(v) for v in best[2]]})
            for c, label, box in dets:
                area_frac = ((box[2] - box[0]) * (box[3] - box[1])) / (fw * fh)
                ring.append(Candidate(c * area_frac, frame.copy(),
                                      datetime.now(timezone.utc), c, label, box))
        else:
            last_dets = 0

        # close the burst: window of silence elapsed -> keep the best frame
        if last_det is not None and ring and now - last_det >= CFG["burst_window"]:
            best = max(ring, key=lambda c: c.score)
            n_burst = len(ring)
            ring.clear()
            last_det = None
            path, box = store_still(best)
            log(f"best still stored: {path} (burst of {n_burst} detection frames, "
                f"best conf {best.conf:.2f})")
            nats_pub.publish({"event": "detection_burst", "camera": CFG["camera"],
                              "label": best.label, "detections": n_burst,
                              "best": {"file": path.name, "path": str(path),
                                       "confidence": round(best.conf, 3),
                                       "frame_ts": best.ts.isoformat(),
                                       "box": box},
                              "detector": "detector.py/1.0"})

        if now - last_hb >= 60:
            last_hb = now
            log_event({"event": "heartbeat", "frames": frames,
                       "fps": round(frames / max(now - t0, 1e-6), 1),
                       "last_dets": last_dets, "stream_ok": stream_ok})
        time.sleep(0.05)   # bound the read loop; the VFR stream paces the rest

    cap.release()
    nats_pub.stop()
    log("stopped")


if __name__ == "__main__":
    main()
