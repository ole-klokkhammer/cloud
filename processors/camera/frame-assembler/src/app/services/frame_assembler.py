import logging
from typing import Dict
import uuid
import cv2
import numpy as np
import env as environment
from datetime import datetime, timezone
from kafka.errors import CorruptRecordError
from kafka.consumer.fetcher import ConsumerRecord
from services.kafka_consumer_service import KafkaConsumerService


class FrameAssembler:
    def __init__(self, topic: str, bootstrap_servers: str, group_id: str):
        self.topic = topic
        self.bootstrap_servers = bootstrap_servers
        self.group_id = group_id

        self.kafka_consumer = KafkaConsumerService(
            topic=self.topic,
            bootstrap_servers=self.bootstrap_servers,
            group_id=self.group_id,
            on_message=self.on_message,
        )

    def start(self):
        logging.info("Starting FrameAssembler...")
        self.kafka_consumer.start()

    def stop(self):
        logging.info("Stopping down FrameAssembler...")
        self.kafka_consumer.stop()

    def on_message(self, message: ConsumerRecord):

        logging.info("Received message from Kafka topic")
        frame_bytes = message.value
        if frame_bytes is None:
            logging.warning("Received None frame, skipping...")
            return

        frame = cv2.imdecode(np.frombuffer(frame_bytes, np.uint8), cv2.IMREAD_COLOR)
        if frame is None:
            logging.error("Failed to decode frame, skipping...")
            return

        parsed_headers = {k: v.decode() for k, v in message.headers}
        timestamp = self.get_timestamp(parsed_headers)
        if timestamp is None:
            raise Exception("No timestamp found in headers, cannot save frame.")

        image_filename = f"{environment.snapshot_dir}/{self.get_filename(timestamp, "jpg")}"
        cv2.imwrite(image_filename, frame)
        logging.info(f"Saved frame to {image_filename}")

    def get_filename(self, timestamp: float, extension: str) -> str:
        return f"frame_{datetime.fromtimestamp(timestamp, tz=timezone.utc).strftime(
            "%Y%m%d_%H%M%S_%f"
        )}_{uuid.uuid4()}.{extension}"

    def get_timestamp(
        self, parsed_headers: Dict[str, bytes], fallback: float | None = None
    ) -> float | None:
        header_timestamp = parsed_headers.get("timestamp")
        if header_timestamp is not None:
            try:
                return float(header_timestamp)
            except ValueError:
                logging.error(
                    f"Invalid timestamp value: {header_timestamp}, returning fallback value {fallback}"
                )
                return fallback
        else:
            logging.warning(
                f"No timestamp found in headers, returning fallback value {fallback}"
            )
            return fallback
