#!/usr/bin/python3

import logging
import signal
import env as environment
from services.motion_detector import MotionDetector

logging.basicConfig(
    level=logging._nameToLevel[environment.log_level.upper()],
    format="%(asctime)s %(levelname)s %(message)s",
)

if __name__ == "__main__":
    motion_detector = MotionDetector()

    def shutdown(signum, frame):
        logging.info(f"Received signal {signum}, shutting down...")
        motion_detector.stop()
        exit(0)

    # Register signal handlers
    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)

    motion_detector.start()
