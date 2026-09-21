#!/usr/bin/env python3
"""Detector service entry point (process coordinator).

Owns everything process-level; each domain module owns its own:
  * capture.py   - CaptureStream daemon (VideoCapture, reconnect policy,
                   stream clock, capture heartbeat beat)
  * detector.py  - Detector pipeline + its own heartbeat (detector beat)
  * nats_pub.py  - NatsPub daemon (auto-reconnecting publisher)
  * mqtt_pub.py  - MqttPub daemon (auto-reconnecting MQTT publisher,
                   only when MQTT_HOST is set)
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
from config import environment
from detector import Detector
from mqtt_pub import MqttPub
from stream import VideoStream


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
    mqtt_pub = MqttPub(
        environment.mqtt_host,
        environment.mqtt_port,
        environment.mqtt_topic,
        user=environment.mqtt_user,
        password=environment.mqtt_pass,
    )
    videoStream = VideoStream(environment.rtsp_url)
    detector = Detector(environment.triton_url, environment.triton_model)

    def on_signal(signum, frame):
        logger.info(f"exit signal {signum} received")
        stop.set()

    signal.signal(signal.SIGTERM, on_signal)
    signal.signal(signal.SIGINT, on_signal)

    mqtt_str = (
        "off"
        if not environment.mqtt_host
        else f"{environment.mqtt_host}:{environment.mqtt_port} "
        f"topic={environment.mqtt_topic}/<camera>"
    )
    logger.info(
        f"starting: triton={environment.triton_url} model={environment.triton_model} "
        f"classes={environment.classes_str} rtsp={environment.rtsp_url} "
        f"input={environment.input_size} conf={environment.min_conf} "
        f"max_fps={environment.max_fps} mqtt={mqtt_str}"
    )

    # triton readiness wait + one-shot health check happen in
    # detector.load() (the constructor is cheap: it only sets state); a
    # hard failure = triton down or its model not loading - fail the
    # process, systemd retries within the window triton usually comes up
    try:
        logger.info(
            f"Loading detector: triton={environment.triton_url} "
            f"model={environment.triton_model} (triton health gate)"
        )
        detector.load()

        logger.info(
            f"Starting MQTT: host={environment.mqtt_host}:{environment.mqtt_port} "
            f"topic={environment.mqtt_topic}/<camera>"
        )
        mqtt_pub.start()

        logger.info("Registering callbacks")
        videoStream.set_frame_callback(detector.on_frame)
        videoStream.set_on_new_session_cbs(detector.new_session)
        detector.set_detection_callbacks(*[mqtt_pub.publish])

        logger.info(
            f"Starting capture: rtsp={environment.rtsp_url} input={environment.input_size} "
            f"conf={environment.min_conf} max_fps={environment.max_fps}"
        )
        videoStream.start()

        logger.info(
            f"Starting detector: triton={environment.triton_url} model={environment.triton_model}"
        )
        detector.start()
    except Exception:
        logger.exception("detector init failed")
        sys.exit(1)

    # main thread's only job: wait for the stop signal, then exit.
    # The capture, detect-hb, NATS, and MQTT threads are all daemons:
    # they die at process exit (the kernel reclaims ffmpeg fds + the
    # CUDA context; mediaMTX, NATS, and HiveMQ just see a TCP close).
    stop.wait()
    logger.info("stopped")


if __name__ == "__main__":
    main()
