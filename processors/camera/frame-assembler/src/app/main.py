#!/usr/bin/python3

import os
import logging
import signal
import sys
import env as environment
from services.frame_assembler import FrameAssembler
from kafka import KafkaConsumer


logging.basicConfig(
    level=logging._nameToLevel[environment.log_level.upper()],
    format="%(asctime)s %(levelname)s %(message)s",
)

logging.info(f"Log level set to: {logging._nameToLevel[environment.log_level.upper()]}")

if __name__ == "__main__":
    logging.info("Starting frame assembler...")

    if not environment.kafka_bootstrap_servers:
        logging.error("KAFKA_BOOTSTRAP_SERVERS environment variable is not set.")
        sys.exit(1)

    frame_assembler = FrameAssembler(
        bootstrap_servers=environment.kafka_bootstrap_servers,
        topic=environment.kafka_topic or "camera_frames",
        group_id=environment.kafka_group_id or "frame_assembler_group",
    )

    def shutdown(signum, frame):
        logging.info("Received shutdown signal, stopping frame assembler...")
        frame_assembler.stop()
        sys.exit(0)

    # Register signal handlers
    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)

    frame_assembler.start()
