"""Stream capture for the detector service.

Owns cv2.VideoCapture (FFMPEG backend, TCP RTSP transport,
CAP_PROP_BUFFERSIZE=1 => latest-frame semantics), reconnects across
stream loss, hands every frame to the frame callback with the frame's
stream time, and emits the 60s heartbeat beats - all on one daemon
thread.

Stream clock: frames are delivered with ts = seconds since the capture
session opened (CAP_PROP_POS_MSEC - the frame's own PTS). Each (re)open
is a new session: on_session hooks fire and the clock restarts, so
downstream time math never mixes two sessions.

Heartbeat: a 60s wall-timer beat (scope "capture": frames, rolling 60s
fps, session, stream health) emitted by this thread, so it keeps
flowing while the stream is down (the "service alive / stream down"
signal). Other scopes run their own timers - the capture module knows
nothing about them (the detector's "detection" beat lives in
detector.py and reports detector activity, not stream health).

This is a daemon thread: it lives until process exit. Stop is handled by
the caller at shutdown - the kernel reclaims the ffmpeg fds and CUDA
context when the process dies, and the stream server just sees a
connection close.
"""

import json
import logging
import os
import threading
import time
from typing import Callable, Dict, List, Optional

import cv2

logger = logging.getLogger(__name__)

# (frame BGR ndarray, stream ts in seconds since session start)
OnFrameCallback = Callable[[object, float], None]

# Force TCP RTSP (UDP drops frames on a lossy LAN). `stimeout` only
# applies to the UDP demuxer; harmless here. Env-overridable.
_TCP_OPTIONS = "rtsp_transport;tcp|stimeout;60000"


class RtspStream(threading.Thread):
    """Owns the VideoCapture; delivers each frame to the frame callback
    with the frame's stream time; emits the 60s heartbeat beats (the
    built-in capture beat plus any registered beats) - all on this thread.

    Reconnect policy: 5s retry while the stream has never come up, 0.5s
    while it was up (fast reconnect); the "stream lost" log fires on the
    first loss and every 12th consecutive failure. Frame-callback
    exceptions are logged (throttled) and never kill this thread.
    """

    def __init__(self, url: str):
        super().__init__(daemon=True, name="capture")
        self._url = url
        self._frame_cb = None
        self._new_session_callbacks: List[Callable[[], None]] = []
        self._cb_errors = 0
        self._ts0_mono = 0.0
        self._session = 0
        self._frames = 0
        self._frames_beat = 0

    # ---- registration (call before start()) -----------------------------

    def set_frame_callback(self, cb: OnFrameCallback) -> "RtspStream":
        """Per-frame callback (frame, stream_ts) - runs on the capture
        thread, so keep it to bookkeeping plus one throttled predict."""
        self._frame_cb = cb
        return self

    def set_on_new_session_callback(self, cb: Callable[[], None]) -> "RtspStream":
        """Called at every open/reconnect - the moment the stream clock
        restarts. Reset per-session state there (windows, rings,
        throttle timers) and set the UTC anchor for stream-time -> UTC
        conversion."""
        self._new_session_callbacks.append(cb)
        return self

    # ---- internals --------------------------------------------------------

    @staticmethod
    def _open(url):
        os.environ.setdefault("OPENCV_FFMPEG_CAPTURE_OPTIONS", _TCP_OPTIONS)
        cap = cv2.VideoCapture(url, cv2.CAP_FFMPEG)
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # low latency: never process a stale frame
        return cap

    def _new_session(self):
        self._session += 1
        self._ts0_mono = time.monotonic()
        for cb in self._new_session_callbacks:
            cb()

    def _stream_ts(self, cap) -> float:
        """Seconds since this session opened: the frame's own PTS
        (CAP_PROP_POS_MSEC). Falls back to the wall clock (same
        since-session semantics) when the property is 0."""
        ms = cap.get(cv2.CAP_PROP_POS_MSEC)
        if ms and ms > 0:
            return ms / 1000.0
        return time.monotonic() - self._ts0_mono

    def _emit_capture_beat(self, fps: float, stream_ok: bool):
        logger.info(
            json.dumps(
                {
                    "event": "heartbeat",
                    "scope": "capture",
                    "frames": self._frames,
                    "fps": round(fps, 1),
                    "session": self._session,
                    "stream_ok": stream_ok,
                },
                separators=(",", ":"),
            )
        )

    def run(self):
        # Runs until process exit: daemon thread, stop is handled at
        # shutdown by the caller - the kernel reclaims the ffmpeg fds and
        # the CUDA context when the process dies.
        cap = self._open(self._url)
        self._new_session()
        stream_ok = False
        lost = 0
        last_beat = time.monotonic()
        while True:
            ret, frame = cap.read()
            if not ret or frame is None:
                lost += 1
                time.sleep(5.0 if not stream_ok else 0.5)
                cap.release()
                cap = self._open(self._url)
                self._new_session()
                stream_ok = False
                if lost == 1 or lost % 12 == 0:
                    logger.warning(
                        f"stream lost - restarting capture (consecutive {lost})"
                    )
            else:
                if not stream_ok:
                    stream_ok = True
                    lost = 0
                    fh, fw = frame.shape[:2]
                    logger.info(f"stream {fw}x{fh}")
                    logger.info(f"capture started ({fw}x{fh} bgr frames)")
                self._frames += 1
                if self._frame_cb:
                    # A callback exception must never kill the capture
                    # thread (the beats run here - a dead thread means no
                    # heartbeats and a zombie service). Log, throttle,
                    # continue - same resilience as the original
                    # process_loop's "Processing error" catch.
                    try:
                        self._frame_cb(frame, self._stream_ts(cap))
                    except Exception:
                        self._cb_errors += 1
                        if self._cb_errors == 1 or self._cb_errors % 50 == 0:
                            logger.error(
                                f"frame callback error (#{self._cb_errors}) - "
                                f"continuing",
                                exc_info=True,
                            )

            # Capture beat on a 60s wall timer; keeps flowing while the
            # stream is down (stream_ok: false). The detection beat has
            # its own timer in detector.py.
            now = time.monotonic()
            if now - last_beat >= 60:
                beat = now - last_beat
                last_beat = now
                fps = (self._frames - self._frames_beat) / max(beat, 1e-6)
                self._frames_beat = self._frames
                self._emit_capture_beat(fps, stream_ok)
