#!/usr/bin/env python3
"""Detector service entry point (process coordinator).

Owns everything process-level; each domain module owns its own:
  * capture.py   - CaptureStream daemon (VideoCapture, reconnect policy,
                   stream clock, capture heartbeat beat)
  * detector.py  - Detector pipeline + DetectionHeartbeat (detector beat)
  * nats_pub.py  - NatsPub daemon (auto-reconnecting publisher)
  * config.py    - env -> typed Environment (attribute access)

main() wires the pieces together and coordinates shutdown: the main
thread's only job is to wait for the stop signal, then tear down. The
capture, detect-hb, and NATS threads are daemons - they run until process
exit and are killed there (the kernel reclaims ffmpeg fds and the CUDA
context; mediaMTX just sees a connection close).
"""

import logging
import os
import signal
import sys
import threading
from pathlib import Path

from capture import CaptureStream
from config import environment
from detector import DetectionHeartbeat, Detector
from nats_pub import NatsPub


def setup_logging():
    """Configure the module logger to stdout (captured by journal / `po`).

    Level is selectable at runtime via DETECTOR_LOG_LEVEL (default DEBUG);
    the `[detector]` prefix is dropped here because journald already tags
    the line with `detector.service`.
    """
    level_name = os.environ.get("DETECTOR_LOG_LEVEL", "DEBUG").upper()
    logging.basicConfig(
        level=getattr(logging, level_name, logging.INFO),
        format="%(asctime)s %(levelname)-7s %(message)s",
        stream=sys.stdout,
    )


def main():
    setup_logging()

    stop = threading.Event()
    logger = logging.getLogger("detector")
    nats_pub = NatsPub(environment.nats_url, environment.nats_subject)
    capture = CaptureStream(environment.rtsp_url)
    detector = Detector(environment.model, environment.device)

    def on_signal(signum, frame):
        logger.info(f"exit signal {signum} received")
        stop.set()

    signal.signal(signal.SIGTERM, on_signal)
    signal.signal(signal.SIGINT, on_signal)

    logger.info(
        f"starting: model={environment.model} device={environment.device} "
        f"classes={environment.classes_str} rtsp={environment.rtsp_url} "
        f"input={environment.input_size} conf={environment.min_conf} max_fps={environment.max_fps}"
    )

    # model load + warm-up happens in detector.load() (the constructor
    # is cheap: it only sets state); a hard failure = bad model path /
    # driver - fail the process before the NATS thread ever starts.
    try:
        logger.info(
            f"Loading detector: model={environment.model} device={environment.device}"
        )
        detector.load()

        logger.info(
            f"Starting NATS: url={environment.nats_url} subject={environment.nats_subject}"
        )
        nats_pub.start()

        logger.info("Registering callbacks")
        capture.set_frame_callback(detector.on_frame)
        capture.on_session(detector.new_session)
        detector.on_detect(nats_pub.publish)

        logger.info(
            f"Starting capture: rtsp={environment.rtsp_url} input={environment.input_size} "
            f"conf={environment.min_conf} max_fps={environment.max_fps}"
        )
        capture.start()

        logger.info(
            f"Starting detector heartbeat: model={environment.model} device={environment.device}"
        )
        det_beat = DetectionHeartbeat(detector)
        det_beat.start()
    except Exception:
        logger.exception("detector init failed")
        sys.exit(1)

    # main thread's only job: wait for the stop signal, then exit.
    # The capture, detect-hb, and NATS threads are all daemons: they
    # die at process exit (the kernel reclaims ffmpeg fds + the CUDA
    # context; mediaMTX and the NATS server just see a TCP close).
    stop.wait()
    logger.info("stopped")


if __name__ == "__main__":
    main()
