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
    with ids) and, when enabled, forwarded to the live-push, which
    streams the annotated frames to mediaMTX only while a tracked
    target is active - so mediaMTX records the annotated path exactly
    when something is happening (idle = dark = nothing recorded); the
    recording IS the footage; no detector-side clip encoding.
  * burst close -> one detection_burst event via the registered
    on_detect callbacks (main.py wires them to MqttPub.publish - the
    domain owns no transport). A burst's footage is a slice of the
    mediaMTX recording; the query side builds the playback URL.

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

Events are the dedupe signal for consumers; the footage lives in the
mediaMTX recording of the annotated stream. Config: env vars, see
detector.env.example.
"""

import json
import logging
import threading
import time
from collections import deque
from datetime import datetime, timedelta, timezone

from config import environment
from services.annotate import draw_boxes
from services.live_push import LivePusher
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
    (the 60s DetectionHeartbeat). The optional live pusher
    (LivePusher - the annotated RTSP re-stream into mediaMTX) is
    constructed + started by main() and injected: main owns its
    lifecycle, this object just hands it painted frames (on_frame)
    and resets it on a new session. on_detect() registers the event
    callbacks (one per transport); from then on `on_frame` and
    `new_session` run only on the capture thread, and the heartbeat
    thread only reads single attributes - so no locking anywhere.
    """

    def __init__(self, server_url: str, model_name: str, live_push: LivePusher | None = None):
        self.min_interval = 1.0 / environment.detector_max_fps
        self._on_detect_callbacks = []  # registered via on_detect(); main wires them
        self._on_detect_cb_errors = 0
        # optional annotated RTSP re-streamer (mediaMTX), started by main();
        # None when DETECTOR_LIVE_PATH is unset - on_frame/new_session no-op it
        self.live_push = live_push
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
        # ---- tracker (created at load, before the capture thread ever
        # touches it)
        self.tracker = Tracker(track_labels=environment.tracker_labels)
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

    def new_session(self):
        """The stream clock just restarted (open/reconnect): reset the
        per-session detection state, and re-anchor the UTC conversion +
        the tracker/live state (the ts domain they key off has changed)."""
        self.ts0 = datetime.now(timezone.utc)
        self.last_det = None
        self.last_infer = -1.0
        self._burst_frames = 0
        self._burst_tracks = {}
        self._burst_best = None
        self.tracker.reset()
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
            logger.info(
                f"burst closed: {n_burst} detection frames, "
                f"{len(self._burst_tracks)} tracks, best {label or 'n/a'} "
                f"{best_conf:.2f} - footage: mediaMTX recording of "
                f"the annotated stream"
            )
            self.last_det = None
            self._burst_frames = 0
            self._burst_tracks = {}
            self._burst_best = None
            self._on_detect(
                {
                    "event": "detection_burst",
                    "camera": environment.event_camera_name,
                    "ts": frame_utc.isoformat(),
                    "label": label,
                    "best_conf": round(best_conf, 3),
                    "detections": n_burst,
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

        # one shared painted copy (all boxes, tracked ones bold + #id),
        # forwarded to the live pusher below when enabled. Empty
        # detection frames still paint (a plain frame) so the annotated
        # stream stays a dense record, not gappy.
        painted = draw_boxes(
            frame,
            res.boxes,
            res.labels,
            [float(res.boxes[i, 4]) for i in range(res.count)],
            ids=ids,
        )
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
