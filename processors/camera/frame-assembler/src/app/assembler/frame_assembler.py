import logging
import signal
import sys
import time
import uuid
import cv2
import numpy as np
from datetime import datetime
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

        video_writer = None
        video_filename = None
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        fps = 20  # Default FPS, can be adjusted or read from message headers
        frame_size = None

        while True:
            try:
                for message in self.kafka_consumer:
                    try:
                        logging.info("Received message from Kafka topic")
                        frame_bytes = message.value
                        if frame_bytes is None:
                            logging.warning("Received None frame, skipping...")
                            continue 
 
                        parsed = {k: v.decode() for k, v in message.headers}
                        recording_id = parsed['recording_id']
                        frame_number = int(parsed['frame_number'])
                        timestamp = float(parsed['timestamp'])
                        fps = float(parsed['fps'])
                        width = int(parsed['width'])
                        height = int(parsed['height'])
                        encoding = parsed['encoding']
 
                        logging.info(f"recording_id: {recording_id}")
                        logging.info(f"frame_number: {frame_number}")
                        # logging.info(f"timestamp: {timestamp}") 
                        # logging.info(f"FPS: {fps}")
                        # logging.info(f"Width: {width}")
                        # logging.info(f"Height: {height}")
                        # logging.info(f"Encoding: {encoding}")  

                        # frame = cv2.imdecode(
                        #     np.frombuffer(frame_bytes, np.uint8), cv2.IMREAD_COLOR
                        # )
                        # if frame is None:
                        #     logging.error("Failed to decode frame, skipping...")
                        #     continue

                        # if frame_size is None: 
                        #    # frame_size = (frame.shape[1], frame.shape[0])
                        #     timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        #     video_filename = f"video_{timestamp}_{uuid.uuid4()}.mp4"
                        #     video_writer = cv2.VideoWriter(
                        #         f"../snapshots/{video_filename}",
                        #         fourcc,
                        #         fps,
                        #         (width, height)  # Use width and height from headers
                        #     )
                        #     logging.info(f"Started new video file: {video_filename}")

                        # if video_writer is not None:
                        #     video_writer.write(frame) 

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
