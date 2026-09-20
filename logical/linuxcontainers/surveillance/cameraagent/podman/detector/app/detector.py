#!/usr/bin/env python3
"""Detection pipeline for the detector service.

Everything in this module is detector domain, no process lifecycle - the
capture stream lives in capture.py, the process coordinator (signals,
thread wiring, teardown) in main.py.

Detector: the per-frame pipeline, driven by CaptureStream's on_frame
callback on the capture thread:
  * every frame: burst-close check (stream-clock window)
  * throttled predict: MAX_FPS on the stream clock; post-failure
    backoff on the wall clock (a cooldown on our side, not a stream
    property)
  * per-frame detection JSON; best-frame ring of 16 Candidates keyed
    on confidence x target-area fraction
  * burst close -> best-frame still (JPEG, <= frame_width wide) + one
    detection_burst event via the registered on_detect callbacks
    (main.py wires them to NatsPub.publish + MqttPub.publish - the
    domain owns no transport).

DetectionHeartbeat: the detector-side 60s beat - its own daemon thread
(started by Detector.start(), so the trimmer's lifecycle belongs to
the state it trims), its own timer (the capture beat in capture.py
reports stream health, this one reports detector activity: last_dets,
dets_60s, idle_s; no stream-health field - that is the capture
beat's job).

Threading: all Detector state is touched only on the capture thread
(on_frame + the on_session hook); the heartbeat thread reads single
attributes (GIL-safe) and sums dets_60s from the append-only event log
- no read-then-reset counter, no locks anywhere.

Stills are the source of truth; NATS events are the dedupe signal for
consumers. Config: env vars, see detector.env.example.
"""

import json
import logging
import sys
import threading
import time
from collections import deque
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path

import cv2
import torch
from ultralytics import YOLO

from config import environment

logger = logging.getLogger("detector")


# ---------------------------------------------------------------- candidates


@dataclass
class Candidate:
    score: float  # conf x target-area fraction
    frame: object  # full-res BGR ndarray (for the still)
    ts: datetime
    conf: float
    label: str
    box: tuple  # xyxy in full-res frame coords


# ---------------------------------------------------------------- pipeline


class Detector:
    """Per-camera detection pipeline.

    Lifecycle: constructed on the main thread (cheap: state only);
    main() calls load() for model load + warm-up (a hard failure
    there exits 1), then start() to bring up this object's own
    daemon thread (the 60s DetectionHeartbeat). on_detect() registers
    the event callbacks (one per transport); from then on `on_frame`
    and `new_session` run only on the capture thread, and the
    heartbeat thread only reads single attributes - so no locking
    anywhere.
    """

    def __init__(self, model_path: str, device: str):
        self.min_interval = 1.0 / environment.max_fps
        self._detect_cbs = []  # registered via on_detect(); main wires them
        self._cb_errors = 0

        # ---- model init (main thread)
        if device == "cuda" and not torch.cuda.is_available():
            # a requested device that we silently downgrade is worth a warning
            logger.warning("cuda requested but unavailable - running on CPU")
            device = "cpu"

        self.device = device
        self.model_path = model_path

        # ---- per-session detection state (reset by new_session)
        self.ring = deque(maxlen=16)  # Candidates of the open burst
        self.last_det = None  # stream ts of the last detection
        self.last_infer = -1.0  # stream ts of the last predict
        self.next_predict_ok = 0.0  # wall clock: post-failure backoff
        # ---- detector-side heartbeat state (read by DetectionHeartbeat)
        self.last_dets = 0  # dets in the last processed frame
        self.last_det_mono = None  # wall clock of the last detection
        self.ts0 = None  # UTC anchor of the current capture session
        # append-only detection event log (wall ts, det count) - read by the
        # DetectionHeartbeat thread (GIL-safe deque ops; no read-then-reset
        # counter to race).
        self.det_events = deque(maxlen=300)

    def load(self):
        try:
            self.model = YOLO(Path(self.model_path))
            self.model.to(self.device)
            logger.info(
                f"device: {self.device} (torch {torch.__version__}, "
                f"cuda {torch.version.cuda})"
            )
        except Exception:
            logger.error("model init failed", exc_info=True)
            raise

        self._warmup()
        logger.info(
            f"model ready: {self.model_path} (device={self.device}, "
            f"input {environment.input_size}x{environment.input_size})"
        )

    def start(self) -> "Detector":
        """Bring up this object's own daemon thread: the 60s
        DetectionHeartbeat (detector-activity beat + the trimmer for
        det_events). Pure daemon like the other workers - no
        stop()/join(), killed at process exit. The heartbeat state it
        trims belongs to this object, so its lifecycle belongs here
        rather than to the process coordinator. Safe to call only
        once, after load()."""
        self._beat = DetectionHeartbeat(self)
        self._beat.start()
        return self

    # ---- event callback (call before the capture loop starts) ---------

    def on_detect(self, *cbs) -> "Detector":
        """Detection-event callbacks: each receives the detection_burst
        payload (dict, same shape NatsPub.publish / MqttPub.publish get).
        They run on the capture thread inside on_frame - keep each to a
        fast, thread-safe enqueue. main.py wires them: NatsPub.publish
        and MqttPub.publish (one callback per transport)."""
        self._detect_cbs.extend(cbs)
        return self

    def _emit(self, payload):
        """Guarded dispatch to the registered callbacks (one per
        transport): an uncaught exception must never kill the capture
        thread (same contract as capture.py's frame-callback guard): log
        #1 + every 50th, keep the loop alive. Each callback is guarded
        separately - a failure in one transport must not stop the
        others. No callbacks registered = events dropped by design."""
        for cb in self._detect_cbs:
            try:
                cb(payload)
            except Exception:
                self._cb_errors += 1
                if self._cb_errors == 1 or self._cb_errors % 50 == 0:
                    logger.error(
                        f"detect callback error (#{self._cb_errors}) from "
                        f"{getattr(cb, '__name__', 'callback')!r} - continuing",
                        exc_info=True,
                    )

    def store_still(self, cand):
        """best frame -> JPEG at <= frame_width wide; returns (path, box-in-still)."""
        img = cand.frame
        fh, fw = img.shape[:2]
        scale = min(1.0, environment.frame_width / fw)
        if scale < 1.0:
            img = cv2.resize(
                img, (int(fw * scale), int(fh * scale)), interpolation=cv2.INTER_AREA
            )
        p = (
            Path(environment.event_dir)
            / f"{cand.label}_{cand.ts.strftime('%Y%m%d_%H%M%S')}.jpg"
        )
        p.parent.mkdir(parents=True, exist_ok=True)
        cv2.imwrite(str(p), img, [int(cv2.IMWRITE_JPEG_QUALITY), 90])
        return p, [round(v * scale) for v in cand.box]

    def new_session(self):
        """The stream clock just restarted (open/reconnect): reset the
        per-session detection state and anchor the UTC conversion."""
        self.ts0 = datetime.now(timezone.utc)
        self.ring.clear()
        self.last_det = None
        self.last_infer = -1.0

    def _warmup(self):
        """Run the production predict path a couple of times before the first
        real frame: same input type (BGR uint8 numpy) and the same args as
        on_frame, so letterbox/preprocess, model kernels, and the NMS +
        class-filter post-process all get warmed. Two iterations: the first
        primes cuDNN + the caching allocator, the second reuses them.
        """
        import numpy as np

        s = environment.input_size
        frame = np.zeros((s, s, 3), dtype=np.uint8)
        for _ in range(2):
            self.model.predict(
                frame,
                imgsz=environment.input_size,
                conf=environment.min_conf,
                iou=0.45,
                classes=environment.classes,
                verbose=False,
            )

    def on_frame(self, frame, ts):
        """One frame in, per-frame pipeline out. Fast by design: heavy work
        is just the throttled predict; everything else is bookkeeping.

        `ts` is the frame's stream time - seconds since the capture
        session opened. Window/throttle math keys off the stream clock,
        not Python's processing clock; a stalled consumer can't skew it.
        """
        now = ts
        fh, fw = frame.shape[:2]

        # close the burst: window of silence elapsed -> keep the best frame.
        # Checked on EVERY frame (incl. throttled ones) so a burst closes
        # within one frame period of the silence window.
        if (
            self.last_det is not None
            and self.ring
            and now - self.last_det >= environment.burst_window
        ):
            best = max(self.ring, key=lambda c: c.score)
            n_burst = len(self.ring)
            self.ring.clear()
            self.last_det = None
            path, box = self.store_still(best)
            logger.info(
                f"best still stored: {path} ({best.label}, "
                f"burst of {n_burst} detection frames, best conf {best.conf:.2f})"
            )
            self._emit(
                {
                    "event": "detection_burst",
                    "camera": environment.camera,
                    "label": best.label,
                    "detections": n_burst,
                    "best": {
                        "file": path.name,
                        "path": str(path),
                        "confidence": round(best.conf, 3),
                        "frame_ts": best.ts.isoformat(),
                        "box": box,
                    },
                    "detector": "detector/1.0",
                }
            )

        if (
            now - self.last_infer < self.min_interval
            or time.monotonic() < self.next_predict_ok
        ):
            return  # throttled / post-failure backoff; capture keeps flowing
        self.last_infer = now

        try:
            res = self.model.predict(
                frame,
                imgsz=environment.input_size,
                conf=environment.min_conf,
                iou=0.45,
                classes=environment.classes,
                verbose=False,
            )[0]
        except Exception:
            # hot-path failures (transient CUDA errors, a GPU-mem spike) must
            # not kill a 24/7 service: log, back off, keep the loop alive.
            logger.error(
                "predict failed on a real frame - backing off 5s", exc_info=True
            )
            self.next_predict_ok = time.monotonic() + 5.0
            return

        dets = []
        if res.boxes is not None and len(res.boxes):
            xyxy = res.boxes.xyxy.cpu().numpy()
            confs = res.boxes.conf.cpu().numpy()
            clss = res.boxes.cls.cpu().numpy().astype(int)
            names = self.model.names
            for (x1, y1, x2, y2), c, cl in zip(xyxy, confs, clss):
                if c >= environment.min_conf and (
                    environment.classes is None or int(cl) in environment.classes
                ):
                    dets.append(
                        (
                            float(c),
                            str(names.get(int(cl), cl)),
                            (float(x1), float(y1), float(x2), float(y2)),
                        )
                    )

        if dets:
            # the frame's own time: session anchor + stream offset
            frame_utc = (
                datetime.now(timezone.utc)
                if self.ts0 is None
                else self.ts0 + timedelta(seconds=now)
            )
            self.last_dets = len(dets)
            self.det_events.append((time.monotonic(), len(dets)))
            self.last_det_mono = time.monotonic()
            best = max(dets, key=lambda d: d[0])
            self.last_det = now
            logger.info(
                json.dumps(
                    {
                        "event": "detection",
                        "camera": environment.camera,
                        "ts": frame_utc.isoformat(),
                        "dets": len(dets),
                        "label": best[1],
                        "best_conf": round(best[0], 3),
                        "bbox": [round(v) for v in best[2]],
                    },
                    separators=(",", ":"),
                )
            )
            for c, label, box in dets:
                area_frac = ((box[2] - box[0]) * (box[3] - box[1])) / (fw * fh)
                self.ring.append(
                    Candidate(
                        c * area_frac,
                        frame.copy(),
                        frame_utc,
                        c,
                        label,
                        box,
                    )
                )
        else:
            self.last_dets = 0


# ---------------------------------------------------------------- detection heartbeat


class DetectionHeartbeat(threading.Thread):
    """Detector-side 60s heartbeat: its own timer, its own place - the
    capture beat (capture.py) reports stream health, this one reports
    detector activity.

    Runs on its own daemon thread; reads Detector attributes written by
    the capture thread. Single-value attribute reads and deque
    append/iterate are GIL-safe, and dets_60s is summed from the
    append-only event log - no read-then-reset counter, so no locking
    anywhere.
    """

    def __init__(self, detector: "Detector"):
        super().__init__(daemon=True, name="detect-hb")
        self._det = detector

    def run(self):
        while True:
            time.sleep(60)
            now = time.monotonic()
            ev = self._det.det_events
            while ev and now - ev[0][0] > 120:
                ev.popleft()
            dets_60s = sum(n for t, n in ev if now - t <= 60)
            idle = (
                None
                if self._det.last_det_mono is None
                else round(now - self._det.last_det_mono, 1)
            )
            logger.info(
                json.dumps(
                    {
                        "event": "heartbeat",
                        "scope": "detection",
                        "last_dets": self._det.last_dets,
                        "dets_60s": dets_60s,
                        "idle_s": idle,
                    },
                    separators=(",", ":"),
                )
            )
