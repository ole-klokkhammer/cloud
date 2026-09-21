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
  * per-frame detection JSON (+ the live tracker's ids for the
    configured labels)
  * every inferred frame gets painted (all boxes; tracked ones bold,
    with ids) into one shared copy: it feeds (a) the rolling .buf
    JPEG ring under clip_dir - the ~20s clip source - and (b) the
    optional live-push, which forwards painted frames to mediaMTX
    (held still when nothing tracked).
  * burst close -> an H.265 clip of the .buf ring (ffmpeg encodes on
    its own thread; the path goes into the event when the *job* is
    queued, not when the file lands) + one detection_burst event via
    the registered on_detect callbacks (main.py wires them to
    MqttPub.publish - the domain owns no transport).

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
import subprocess
import threading
import time
from collections import deque
from datetime import datetime, timedelta, timezone
from pathlib import Path

import cv2

from config import environment
from services.annotate import draw_boxes
from services.tracker import Tracker
from services.triton_client import TritonClient

logger = logging.getLogger("detector")


# ---------------------------------------------------------------- pipeline


class Detector:
    """Per-camera detection pipeline.

    Lifecycle: constructed on the main thread (cheap: the triton
    client holds no model - the triton container owns the .pt + the
    GPU, this process just talks gRPC to it); main() calls load() for
    the triton readiness wait + a one-shot end-to-end health check (a
    hard failure there exits 1), then start() to bring up this object's
    own daemon thread
    (the 60s DetectionHeartbeat). on_detect() registers the event
    callbacks (one per transport); from then on `on_frame` and
    `new_session` run only on the capture thread, and the heartbeat
    thread only reads single attributes - so no locking anywhere.
    """

    def __init__(self, server_url: str, model_name: str):
        self.min_interval = 1.0 / environment.detector_max_fps
        self._on_detect_callbacks = []  # registered via on_detect(); main wires them
        self._on_detect_cb_errors = 0
        self.tritonClient = TritonClient(
            server_url,
            model_name,
            imgsz=environment.triton_input_size,
            names=environment.triton_class_labels,
            family=environment.triton_model_family,
        )

    def load(self):
        """Startup health gate (the model itself lives in the triton
        container, so there is nothing for this process to load): wait
        for triton to be ready - its model load takes ~30-60s after a
        boot - then one end-to-end sanity inference. A hard failure =
        triton down or its model failing to load; main() exits 1 and
        systemd retries within the window triton usually comes up."""
        self.tritonClient.load(
            conf=environment.triton_min_conf,
            iou=environment.triton_iou,
            classes=environment.triton_class_filter,
        )

        # ---- per-session detection state (reset by new_session)
        self.last_det = None  # stream ts of the last detection
        self.last_infer = -1.0  # stream ts of the last predict
        self.next_predict_ok = 0.0  # wall clock: post-failure backoff
        self._burst_frames = 0  # detection frames in the open burst window
        self._burst_tracks: dict[int, str] = {}  # track id -> label, seen in burst
        self._burst_best = None  # (conf, label) of the best det in the burst
        # ---- tracker + clip buffers (created at load so the dirs exist
        # before the capture thread ever touches them)
        self.tracker = Tracker(track_labels=environment.tracker_labels)
        self.buf_dir = str(Path(environment.detector_clip_dir) / ".buf")
        Path(self.buf_dir).mkdir(parents=True, exist_ok=True)
        n_buf = max(
            4, int(environment.detector_clip_seconds * environment.detector_max_fps)
        )
        self._buf_seqs: deque[int] = deque(
            maxlen=n_buf
        )  # painted-frame seq numbers, oldest left -> newest right
        self._seq = 0  # monotonic painted-frame counter (zero-padded file names)
        # optional live streamer: painted frames loop as an RTSP push into
        # mediaMTX (the path is auto-created on publish); when nothing
        # tracked, the last painted frame holds still. None when
        # DETECTOR_LIVE_PATH is empty.
        self.live_push = None
        if environment.detector_live_path:
            from services.live_push import LivePusher

            self.live_push = LivePusher(
                environment.detector_live_path,
                fps=environment.detector_max_fps,
                hold_s=environment.detector_live_hold,
            )
            self.live_push.start()
        # ---- detector-side heartbeat state (read by DetectionHeartbeat)
        self.last_dets = 0  # dets in the last processed frame
        self.last_det_mono = None  # wall clock of the last detection
        self.ts0 = None  # UTC anchor of the current capture session
        # append-only detection event log (wall ts, det count) - read by the
        # DetectionHeartbeat thread (GIL-safe deque ops; no read-then-reset
        # counter to race).
        self.det_events = deque(maxlen=300)

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

    def set_on_detect_callbacks(self, *cbs) -> "Detector":
        """Detection-event callbacks: each receives the detection_burst
        payload (dict, same shape NatsPub.publish / MqttPub.publish get).
        They run on the capture thread inside on_frame - keep each to a
        fast, thread-safe enqueue. main.py wires them: NatsPub.publish
        and MqttPub.publish (one callback per transport)."""
        self._on_detect_callbacks.extend(cbs)
        return self

    def _on_detect(self, payload):
        """Guarded dispatch to the registered callbacks (one per
        transport): an uncaught exception must never kill the capture
        thread (same contract as capture.py's frame-callback guard): log
        #1 + every 50th, keep the loop alive. Each callback is guarded
        separately - a failure in one transport must not stop the
        others. No callbacks registered = events dropped by design."""
        for cb in self._on_detect_callbacks:
            try:
                cb(payload)
            except Exception:
                self._on_detect_cb_errors += 1
                if (
                    self._on_detect_cb_errors == 1
                    or self._on_detect_cb_errors % 50 == 0
                ):
                    logger.error(
                        f"detect callback error (#{self._on_detect_cb_errors}) from "
                        f"{getattr(cb, '__name__', 'callback')!r} - continuing",
                        exc_info=True,
                    )

    def _save_buf_frame(self, frame):
        """Persist one painted full-res frame into the rolling .buf ring
        (a JPEG per frame; the oldest is evicted automatically). Returns
        the frame's seq number - the clip encoder stitches a seq RANGE of
        these together, so the ring is the clip source, not per-burst
        stills. When the ring is full each new frame evicts the oldest,
        and that file is unlinked too - otherwise the ring would leak
        disk at ~full-res-JPEG rate forever."""
        seq = self._seq
        self._seq += 1
        out = Path(self.buf_dir) / f"{seq:08d}.jpg"
        cv2.imwrite(str(out), frame, [int(cv2.IMWRITE_JPEG_QUALITY), 85])
        # if this append overflows the ring, the oldest tracked seq is the
        # one being dropped - its .jpg goes with it
        evicted = (
            self._buf_seqs[0] if len(self._buf_seqs) >= self._buf_seqs.maxlen else None
        )
        self._buf_seqs.append(seq)
        if evicted is not None:
            try:
                (Path(self.buf_dir) / f"{evicted:08d}.jpg").unlink()
            except OSError:
                pass
        return seq

    def _clear_buf(self):
        """Drop every ring frame (a new session: the .jpg files are the
        previous session's - never clip across a stream restart)."""
        for seq in self._buf_seqs:
            try:
                (Path(self.buf_dir) / f"{seq:08d}.jpg").unlink()
            except OSError:
                pass
        self._buf_seqs.clear()

    def _render_clip(self, frame_utc, tracks) -> dict:
        """Encode the .buf ring (up to DETECTOR_CLIP_SECONDS of painted
        frames) into an H.265 MP4 under the clip dir, ffmpeg on its own
        (subprocess) so the capture thread just enqueues the event.

        Returns the event's `clip` sub-payload. Runs on the capture thread
        at burst-close (not on the 10fps hot path), so a ~15MB encode
        there is acceptable; the path is into the dir the ffmpeg job
        fills, not the finished file. `tracks` is a list of (id, label)
        for every tracked target seen during the open burst (deduped:
        first-seen label wins, so a flicker can't mislabel an id).
        """
        clip_dir = Path(environment.detector_clip_dir)
        clip_dir.mkdir(parents=True, exist_ok=True)
        name = (
            f"{environment.event_camera_name}_{frame_utc.strftime('%Y%m%d_%H%M%S')}.mp4"
        )
        clip_path = clip_dir / name

        # a burst can't close with an empty ring (no inference happened in
        # this session yet) - nothing to encode. The event still fires; it
        # just carries no clip.
        if not self._buf_seqs:
            return {"error": "empty"}

        # the ring holds the newest n_buf seqs oldest->newest; encode that
        # range with the image2 demuxer. A seq gap can't happen within the
        # ring (a single .buf dir, appended in order), so -start_number +
        # a frame-rate on the input is all ffmpeg needs.
        lo, hi = self._buf_seqs[0], self._buf_seqs[-1]
        fps = environment.detector_max_fps
        cmd = [
            "ffmpeg",
            "-hide_banner",
            "-loglevel",
            "error",
            "-framerate",
            str(fps),
            "-start_number",
            str(lo),
            "-i",
            f"{self.buf_dir}/%08d.jpg",
            "-frames:v",
            str(hi - lo + 1),
            "-c:v",
            "libx265",
            "-preset",
            "fast",
            "-pix_fmt",
            "yuv420p",
            "-b:v",
            "6M",
            "-tag:v",
            "hvc1",  # Apple/QuickTime compatibility in the mp4 wrapper
            "-y",
            str(clip_path),
        ]
        track_payload = [{"id": tid, "label": lab} for tid, lab in sorted(set(tracks))]
        try:
            subprocess.run(cmd, capture_output=True, check=False, timeout=120)
        except (subprocess.SubprocessError, OSError):
            logger.error("clip encode failed - no clip for this burst", exc_info=True)
            return {"file": name, "path": str(clip_path), "error": "encode"}
        n = hi - lo + 1 if lo <= hi else 0
        return {
            "file": name,
            "path": str(clip_path),
            "duration_s": round(n / fps, 1) if fps else 0.0,
            "fps": fps,
            "tracks": track_payload,
        }

    def new_session(self):
        """The stream clock just restarted (open/reconnect): reset the
        per-session detection state, clear the previous session's ring
        frames, and re-anchor the UTC conversion + the tracker/live state
        (the ts domain they key off has changed)."""
        self.ts0 = datetime.now(timezone.utc)
        self.last_det = None
        self.last_infer = -1.0
        self._burst_frames = 0
        self._burst_tracks = {}
        self._burst_best = None
        self._seq = 0
        self.tracker.reset()
        self._clear_buf()
        if self.live_push is not None:
            self.live_push.on_new_session()

    def on_frame(self, frame, ts):
        """One frame in, per-frame pipeline out. Fast by design: heavy work
        is just the throttled predict; everything else is bookkeeping.

        `ts` is the frame's stream time - seconds since the capture
        session opened. Window/throttle math keys off the stream clock,
        not Python's processing clock; a stalled consumer can't skew it.
        """
        now = ts

        # close the burst: a window of silence elapsed after a detection.
        # Checked on EVERY frame (incl. throttled ones) so a burst closes
        # within one frame period of the silence window.
        if (
            self._burst_frames > 0
            and self.last_det is not None
            and now - self.last_det >= environment.detector_burst_window
        ):
            frame_utc = (
                datetime.now(timezone.utc)
                if self.ts0 is None
                else self.ts0 + timedelta(seconds=now)
            )
            n_burst = self._burst_frames
            best_conf, label = self._burst_best or (0.0, None)
            clip = self._render_clip(frame_utc, self._burst_tracks.items())
            logger.info(
                f"burst clip stored: {clip.get('path', 'n/a')} ({n_burst} detection "
                f"frames, {clip.get('duration_s', 0)}s, "
                f"{len(clip.get('tracks', []))} tracks, best {label or 'n/a'} "
                f"{best_conf:.2f})"
            )
            self.last_det = None
            self._burst_frames = 0
            self._burst_tracks = {}
            self._burst_best = None
            self._on_detect(
                {
                    "event": "detection_burst",
                    "camera": environment.event_camera_name,
                    "label": label,
                    "best_conf": round(best_conf, 3),
                    "detections": n_burst,
                    "clip": clip,
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
            # the client already applied conf + NMS + the class filter
            # around the remote inference - no re-filtering here
            res = self.tritonClient.predict(
                frame,
                conf=environment.triton_min_conf,
                iou=environment.triton_iou,
                classes=environment.triton_class_filter,
            )
        except Exception:
            # hot-path failures (triton down, a transient network error)
            # must not kill a 24/7 service: log, back off, keep the loop
            # alive - triton comes back and the next frame is just in.
            logger.error(
                "predict failed on a real frame - backing off 5s", exc_info=True
            )
            self.next_predict_ok = time.monotonic() + 5.0
            return

        dets = [
            (
                float(res.boxes[i, 4]),
                res.labels[i],
                (
                    float(res.boxes[i, 0]),
                    float(res.boxes[i, 1]),
                    float(res.boxes[i, 2]),
                    float(res.boxes[i, 3]),
                ),
            )
            for i in range(res.count)
        ]

        # tracker ALWAYS sees this frame (even a detless one) - that is how
        # stale tracks get pruned. ids align to dets (== res box order).
        ids, had_active = self.tracker.update(dets, now)

        # one shared painted copy (all boxes, tracked ones bold + #id): it
        # feeds the rolling clip ring and the live pusher below. Empty
        # detection frames still paint (a plain frame) so the ring stays a
        # dense 20s of real footage, not gappy.
        painted = draw_boxes(
            frame,
            res.boxes,
            res.labels,
            [float(res.boxes[i, 4]) for i in range(res.count)],
            ids=ids,
        )
        self._save_buf_frame(painted)
        if self.live_push is not None:
            self.live_push.offer(painted, now, had_active)

        # which of this frame's boxes are tracked targets (for the log).
        frame_tracks = [
            {"id": ids[i], "label": res.labels[i]}
            for i in range(res.count)
            if ids[i] is not None
        ]

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
            # the burst's overall best det (label + conf the event reports)
            if self._burst_best is None or best[0] > self._burst_best[0]:
                self._burst_best = (best[0], best[1])
            # fold this frame's tracked ids into the open burst (first-seen
            # label wins, so a 1-frame flicker can't mislabel an id).
            for t in frame_tracks:
                self._burst_tracks.setdefault(t["id"], t["label"])
            self._burst_frames += 1
            logger.info(
                json.dumps(
                    {
                        "event": "detection",
                        "camera": environment.event_camera_name,
                        "ts": frame_utc.isoformat(),
                        "dets": len(dets),
                        "label": best[1],
                        "best_conf": round(best[0], 3),
                        "bbox": [round(v) for v in best[2]],
                        "tracks": frame_tracks,
                    },
                    separators=(",", ":"),
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
