import logging
import signal
import sys
import time
import uuid
import cv2
import numpy as np
from datetime import datetime, timezone
from kafka.errors import CorruptRecordError


class FrameAssembler:
    def __init__(self, kafka_consumer=None):
        self.kafka_consumer = kafka_consumer

    def shutdown(self, signum=None, frame=None):
        logging.info("Shutting down FrameAssembler...") 
        if self.kafka_consumer is not None: 
            self.kafka_consumer.close()
            exit(0)

    def run(self):
        logging.info("Starting frame assembler...")

        # Register signal handlers
        signal.signal(signal.SIGINT, self.shutdown)
        signal.signal(signal.SIGTERM, self.shutdown)

        if not self.kafka_consumer:
            raise ValueError("Kafka consumer is not initialized.")
   

        while True:
            try:
                for message in self.kafka_consumer:
                    try:
                        logging.info("Received message from Kafka topic")
                        frame_bytes = message.value
                        if frame_bytes is None:
                            logging.warning("Received None frame, skipping...")
                            continue 
 
                        parsed_headers = {k: v.decode() for k, v in message.headers} 
                        timestamp = float(parsed_headers['timestamp'])
                        fps = float(parsed_headers['fps'])
                        width = int(parsed_headers['width'])
                        height = int(parsed_headers['height'])
                        encoding = parsed_headers['encoding']
  
                        # logging.info(f"timestamp: {timestamp}") 
                        # logging.info(f"FPS: {fps}")
                        # logging.info(f"Width: {width}")
                        # logging.info(f"Height: {height}")
                        # logging.info(f"Encoding: {encoding}")  

                        frame = cv2.imdecode(
                            np.frombuffer(frame_bytes, np.uint8), cv2.IMREAD_COLOR
                        )
                        if frame is None:
                            logging.error("Failed to decode frame, skipping...")
                            continue

                        # Save each frame as an image file instead of writing to video
                        timestamp_str = datetime.fromtimestamp(timestamp, tz=timezone.utc).strftime("%Y%m%d_%H%M%S_%f")
                        image_filename = f"../snapshots/frame_{timestamp_str}_{uuid.uuid4()}.jpg"
                        cv2.imwrite(image_filename, frame)
                        logging.info(f"Saved frame to {image_filename}")

                        # Commit the message after successful processing
                        self.kafka_consumer.commit()
                    except Exception as e:
                        logging.error(f"Error processing message: {e}")
                        continue
            except CorruptRecordError as e:
                logging.error(f"Corrupt record encountered, skipping: {e}")
                for tp in self.kafka_consumer.assignment():
                    current_offset = self.kafka_consumer.position(tp)
                    self.kafka_consumer.seek(tp, current_offset + 1)
                continue
