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
    def __init__(
        self,
        topic: str,
        bootstrap_servers: str,
        group_id: str,
        fps: int = 10,
        chunk_gap_seconds: int = 5 * 60,  # Default to 5 minutes
    ):
        self.topic = topic
        self.bootstrap_servers = bootstrap_servers
        self.group_id = group_id
        self.fps = fps
        self.chunk_gap_seconds = chunk_gap_seconds

        self.video_writer = None
        self.prev_timestamp = None

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
        if self.video_writer is not None:
            self.video_writer.release()
            self.video_writer = None
            logging.info("Finalized last video chunk.")

    def on_message(self, message: ConsumerRecord):

        logging.info("Received message from Kafka topic")
        frame_bytes = message.value
        if frame_bytes is None:
            raise Exception("Received None frame_bytes from Kafka message")

        frame = cv2.imdecode(np.frombuffer(frame_bytes, np.uint8), cv2.IMREAD_COLOR)
        if frame is None:
            raise Exception("Failed to decode frame")

        parsed_headers = {k: v.decode() for k, v in message.headers}
        timestamp = self.get_timestamp(parsed_headers)
        if timestamp is None:
            raise Exception("No timestamp found in headers, cannot save frame.")

        # file_path = (
        # f"{environment.snapshot_dir}/{self.get_filename(timestamp, "jpg")}"
        # )
        # cv2.imwrite(file_path, frame)
        # logging.info(f"Saved frame to {file_path}")

        # Check if we need to start a new chunk
        start_new_chunk = False
        if self.video_writer is None:
            start_new_chunk = True
        elif (
            self.prev_timestamp is not None
            and (timestamp - self.prev_timestamp) >= self.chunk_gap_seconds
        ):
            # Close previous chunk
            self.video_writer.release()
            self.video_writer = None
            logging.info("Closed video chunk due to timestamp gap.")
            start_new_chunk = True

        if start_new_chunk:
            self.frame_size = (frame.shape[1], frame.shape[0])
            chunk_filename = (
                f"{environment.snapshot_dir}/{self.get_filename(timestamp, "avi")}"
            )
            fourcc = cv2.VideoWriter_fourcc(*"XVID") # Or HEVC, but ffmpeg support it
            self.video_writer = cv2.VideoWriter(
                chunk_filename, fourcc, self.fps, self.frame_size
            )
            logging.info(f"Started new video chunk: {chunk_filename}")

        self.video_writer.write(frame)
        self.prev_timestamp = timestamp
        logging.info("Frame written to video chunk.")

    def get_filename(self, timestamp: float, extension: str) -> str:
        return f"frame_{datetime.fromtimestamp(timestamp, tz=timezone.utc).strftime(
            "%Y%m%d_%H%M%S_%f"
        )}.{extension}"

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
