#!/usr/bin/env python3
"""Detector service entry point (process coordinator).

Owns everything process-level; each domain module owns its own:
  * capture.py   - CaptureStream daemon (VideoCapture, reconnect policy,
                   stream clock, capture heartbeat beat)
  * detector.py  - Detector pipeline + its own heartbeat (detector beat)
  * live_push.py - LivePusher daemon (annotated RTSP re-stream into
                   mediaMTX, only when DETECTOR_LIVE_PATH is set)
  * mqtt_pub.py  - MqttPub daemon (auto-reconnecting MQTT publisher,
                   only when MQTT_HOST is set)
  * config.py    - env -> typed Environment (attribute access)

main() wires the pieces together and coordinates shutdown: the main
thread's only job is to wait for the stop signal, then tear down. The
capture, detect-hb, mqtt, and live-push threads are daemons - they run
until process exit and are killed there (the kernel reclaims ffmpeg fds
and the CUDA context; mediaMTX just sees a connection close).
"""

import logging
import os
import signal
import sys
import threading
from config import environment
from services.detector import Detector
from services.live_push import LivePusher
from services.mqtt_pub import MqttPub
from services.rtsp import RtspStream


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
    videoStream = RtspStream(environment.rtsp_url)
    livePusher = LivePusher(
        environment.detector_live_path,
        fps=environment.detector_max_fps,
        hold_s=environment.detector_live_hold,
    )
    detector = Detector(environment.triton_url, environment.triton_model, livePusher)

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
    live_str = (
        "off" if not environment.detector_live_path else environment.detector_live_path
    )
    logger.info(
        f"starting: triton={environment.triton_url} model={environment.triton_model} "
        f"family={environment.triton_model_family} "
        f"class_filter={environment.class_filter_str} rtsp={environment.rtsp_url} "
        f"input={environment.triton_input_size} conf={environment.triton_min_conf} "
        f"max_fps={environment.detector_max_fps} mqtt={mqtt_str} live={live_str}"
    )

    try:
        logger.info(
            f"Loading detector: triton={environment.triton_url} "
            f"model={environment.triton_model} (triton health gate)"
        )
        detector.load()

        logger.info(f"Starting live push: {environment.detector_live_path}")
        livePusher.start()

        logger.info(
            f"Starting MQTT: host={environment.mqtt_host}:{environment.mqtt_port} "
            f"topic={environment.mqtt_topic}/<camera>"
        )
        mqtt_pub.start()

        logger.info("Registering callbacks")
        videoStream.set_frame_callback(detector.on_frame)
        videoStream.set_on_new_session_callback(detector.new_session)
        detector.set_on_detect_callbacks(*[mqtt_pub.publish])

        logger.info(
            f"Starting capture: rtsp={environment.rtsp_url} input={environment.triton_input_size} "
            f"conf={environment.triton_min_conf} max_fps={environment.detector_max_fps}"
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
    # The capture, detect-hb, mqtt, and live-push threads are all daemons:
    # they die at process exit (the kernel reclaims ffmpeg fds + the
    # CUDA context; mediaMTX and HiveMQ just see a TCP close).
    stop.wait()
    logger.info("stopped")


if __name__ == "__main__":
    main()
