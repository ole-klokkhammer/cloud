#!/usr/bin/env python3
"""Live annotated RTSP push into mediaMTX (the detector's re-stream).

One ffmpeg subprocess (H.264, low-latency) with a raw-BGR pipe input;
the capture thread hands painted frames in via offer() (an attribute
swap under the GIL - no locks, same convention as the heartbeat reads).

Behavior (activity-gated - the push is the recording source, so the
recording follows the push):
  * while a tracked target is active, or within hold_s of the last one
    -> ffmpeg runs and each tick sends the newest painted frame;
    mediaMTX records the path for as long as the publisher is connected.
  * when idle (no tracked target within hold_s) -> ffmpeg is stopped:
    the RTSP path then has no publisher, so mediaMTX records nothing
    and no bandwidth is consumed. The path stays defined (configured
    in mediamtx.yml) but dark.
  * when activity resumes -> ffmpeg respawns (a fresh H.264 session
    whose first frame is an IDR) and recording resumes; each burst is
    its own recording segment.
  * ffmpeg exits (mediaMTX restart, network blip) -> respawn with a
    backoff; a dims change (stream re-negotiated) -> respawn with the
    new size.

H.264 (not H.265) deliberately: H.265-over-RTSP is fiddly (RTP
fragmentation + keyframe spacing), H.264 zerolatency is bulletproof
for live players.
"""

import logging
import subprocess
import threading
import time
from collections import deque

logger = logging.getLogger("detector")


class LivePusher(threading.Thread):
    """A daemon thread that paces painted frames into ffmpeg's stdin and
    ffmpeg pushes the result to an RTSP path on mediaMTX (the path is
    auto-created by mediaMTX on first publish - no mediaMTX config
    change needed)."""

    def __init__(self, rtsp_url: str, fps: float = 10.0, hold_s: float = 3.0):
        super().__init__(daemon=True, name="live-push")
        self.rtsp_url = rtsp_url
        self.fps = fps
        self.hold_s = hold_s
        # shared state (written on the capture thread, read here - single
        # attribute swaps, GIL-safe, no read-then-modify sequence)
        self._latest = None  # newest painted frame (BGR ndarray)
        self._latest_ts = 0.0  # stream ts of _latest
        self._last_active_ts = None  # stream ts of the last frame that had a
        # tracked target (None = not active yet)
        self._last_sent = None  # last frame actually written to ffmpeg
        self._dims = None  # (h, w) fed to the running ffmpeg
        self._repeats = 0  # consecutive unexpected ffmpeg deaths (a clean
        # push of >= 60 ticks resets it, so it is "in a row", not total)
        self._ok = 0  # consecutive clean ticks since the last death
        self._err_tail: deque[str] = deque(maxlen=8)  # latest ffmpeg stderr lines
        self._err_thread: threading.Thread | None = None

    # ---- capture-thread interface --------------------------------------

    def offer(self, frame, ts: float, active: bool):
        """One painted frame from the capture thread. `active` = this
        inferred frame had a tracked target (a tracked-label match).
        Cheap by design: attribute stores, no IO."""
        self._latest = frame
        self._latest_ts = ts
        if active:
            self._last_active_ts = ts

    def on_new_session(self):
        """The stream clock restarted: the ts domain changed, so the
        activity marker is invalid - the push goes dark until tracking
        activity reappears."""
        self._last_active_ts = None

    # ---- run loop --------------------------------------------------------

    def _active_now(self):
        """True while a tracked target is active, i.e. the last frame that
        had one is within hold_s on the stream clock. Reads only shared
        attribute values written by the capture thread (GIL-safe)."""
        return (
            self._last_active_ts is not None
            and self._latest is not None
            and (self._latest_ts - self._last_active_ts) <= self.hold_s
        )

    def run(self):
        while True:
            # idle gate: only publish while a tracked target is active (or
            # within hold_s of the last one). No publisher = mediaMTX has
            # no stream on this path, so it records nothing and no
            # bandwidth is spent while idle.
            while not self._active_now():
                time.sleep(0.2)

            # activity just resumed: wait for a painted frame (dims known)
            while self._latest is None:
                time.sleep(0.2)
            h, w = self._latest.shape[:2]
            self._dims = (h, w)
            self._ok = 0
            proc = self._spawn(h, w)
            next_tick = time.monotonic()
            intentional = False
            while True:
                # a stream re-resolution changes dims -> respawn ffmpeg
                if self._latest is not None:
                    nh, nw = self._latest.shape[:2]
                    if (nh, nw) != self._dims:
                        logger.info(
                            f"live push: dims changed {self._dims} -> ({nh},{nw}) - respawning ffmpeg"
                        )
                        intentional = True
                        break
                # idle: last tracked frame older than hold_s -> stop
                # publishing; the path goes dark and mediaMTX records nothing
                if not self._active_now():
                    logger.info(
                        f"live push: idle ({self.hold_s:.0f}s without a tracked target) "
                        f"- stopping ffmpeg, path goes dark"
                    )
                    intentional = True
                    break
                frame = self._pick()
                if frame is not None:
                    try:
                        # one 2560**2 BGR frame; blocking writes release the
                        # GIL, ffmpeg drains at the same rate
                        proc.stdin.write(frame.tobytes())
                        self._last_sent = frame
                        # a clean run of ticks proves the push is healthy:
                        # reset the consecutive-death counter
                        self._ok += 1
                        if self._ok >= 60:
                            self._repeats = 0
                            self._ok = 0
                    except (BrokenPipeError, OSError):
                        break  # ffmpeg died mid-write
                # pace: one frame per 1/fps wall seconds
                next_tick += 1.0 / self.fps
                if next_tick > time.monotonic():
                    time.sleep(next_tick - time.monotonic())
                if proc.poll() is not None:
                    break  # ffmpeg died on its own

            rc, err_lines = self._reap(proc)

            if intentional:
                # idle or dims change: back to the idle gate, no backoff
                continue

            # ffmpeg died unexpectedly: bounded respawns, then give up the
            # thread (the detector keeps working - the live path goes dark)
            self._ok = 0
            self._repeats += 1
            reason = " | ".join(err_lines[-4:]) if err_lines else "no stderr captured"
            if self._repeats <= 30:
                logger.warning(
                    f"live push: ffmpeg exited (rc={rc}); ffmpeg: {reason} - "
                    f"respawning in 5s (#{self._repeats})"
                )
                time.sleep(5.0)
            else:
                logger.critical(
                    f"live push: 30 respawns failed (last rc={rc}; ffmpeg: {reason}) "
                    f"- thread giving up"
                )
                return

    def _reap(self, proc):
        """Drain ffmpeg's stderr tail and wait for its exit. A terminate is
        sent first (a clean stop for intentional exits; a no-op if it already
        died on its own). Returns (returncode, last stderr lines)."""
        if self._err_thread is not None:
            self._err_thread.join(timeout=1.0)  # let the last stderr drain
            self._err_thread = None
        try:
            proc.terminate()
        except OSError:
            pass
        try:
            proc.stdin.close()
        except OSError:
            pass
        try:
            proc.wait(timeout=5)  # real exit code, not the None of a killed proc
        except subprocess.TimeoutExpired:
            try:
                proc.kill()
            except OSError:
                pass
        return proc.returncode, [l for l in self._err_tail if l]

    def _pick(self):
        """The frame for this tick: the newest painted frame while the
        push is active. On a dims change (respawn is handled a tick
        later) it re-sends the last-sent frame of the old size."""
        if self._last_sent is None:
            return self._latest
        active = (
            self._last_active_ts is not None
            and self._latest is not None
            and (self._latest_ts - self._last_active_ts) <= self.hold_s
        )
        if active and self._latest is not None:
            # only feed dims we spawned for: a dims-change is handled
            # one tick before (respawn) - this tick re-sends the last
            # sent frame of the old size if the new frame differs
            if self._latest.shape[:2] != self._dims:
                return self._last_sent
            return self._latest
        # not active: not reached in the normal flow (the idle gate stops
        # the push before this tick) - keep the last-sent frame as a safety
        return self._last_sent

    def _spawn(self, h: int, w: int) -> subprocess.Popen:
        cmd = [
            "ffmpeg",
            "-hide_banner",
            "-loglevel",
            "error",
            "-f",
            "rawvideo",
            "-pix_fmt",
            "bgr24",
            "-s",
            f"{w}x{h}",
            "-r",
            str(self.fps),
            "-i",
            "pipe:0",
            "-an",
            "-c:v",
            "libx264",
            "-preset",
            "veryfast",
            "-tune",
            "zerolatency",
            "-b:v",
            "4M",
            "-g",
            str(int(self.fps * 2)),  # ~2s GOP for the RTSP keyframes
            "-pix_fmt",
            "yuv420p",
            "-f",
            "rtsp",
            self.rtsp_url,
        ]
        logger.info(f"live push: {self.rtsp_url} ({w}x{h} @ {self.fps}fps)")
        proc = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,  # binary: we write frame.tobytes()
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,  # binary: _drain_stderr decodes the lines
        )
        # ffmpeg's stderr goes to a rolling tail (a drain thread), so a death
        # can be logged as a reason instead of a bare "rc=None".
        self._err_tail.clear()
        self._err_thread = threading.Thread(
            target=self._drain_stderr, args=(proc.stderr, self._err_tail), daemon=True
        )
        self._err_thread.start()
        return proc

    def _drain_stderr(self, err, tail: deque):
        """Read ffmpeg's stderr off the pipe so it never blocks and we keep
        the last few lines for the next death log. Err is a binary stream
        (Popen has no text mode - stdin must stay binary for frame.tobytes()),
        so each line is utf-8-decoded here."""
        for line in err:
            text = line.decode("utf-8", "replace").rstrip()
            if text:
                tail.append(text)
        try:
            err.close()
        except OSError:
            pass
