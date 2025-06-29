#!/usr/bin/python3

from dataclasses import dataclass
import os
import logging
import signal
import time
from typing import TypedDict
import cv2
import env as environment
from services.object_detector import CoralTPUObjectDetectorService
from services.video_streamer import VideoStreamerService
from services.restreamer import FfmpegReStreamerService
from utils.bg_subtractor_mog2 import BackgroundSubtractorMOG2
from kafka import KafkaProducer


class MotionDetectorService:
    def __init__(
        self,
        stream_url: str,
        detector_frame_size: tuple[int, int] = (640, 480),
        output_frame_size: tuple[int, int] = (640, 480),
        kafka_topic: str | None = None,
        kafka_producer: KafkaProducer | None = None,
        object_detector: CoralTPUObjectDetectorService | None = None,
    ):
        self.stream_url = stream_url
        self.detector_frame_size = detector_frame_size
        self.output_frame_size = output_frame_size

        self.camera_id = self.stream_url.rsplit("/", 1)[-1]
        self.restreamer_frame_size = output_frame_size
        self.restreamer_stream_name = self.camera_id
        self.kafka_topic = kafka_topic

        ###############################################
        # Initialize the video streamer components
        ###############################################

        self.video_streamer = VideoStreamerService(
            stream_url=self.stream_url, on_frame=self.on_frame
        )
        self.background_subtractor = BackgroundSubtractorMOG2(
            history=100, varThreshold=5, detectShadows=True, shadowThreshold=0.5
        )
        self.kafka_producer = kafka_producer
        self.object_detector = object_detector

        # Initialize the restreamer if enabled
        if environment.enable_restreamer:
            logging.info("Restreamer is enabled.")
            self.restreamer = FfmpegReStreamerService(
                stream_name=self.restreamer_stream_name,
                frame_size=self.restreamer_frame_size,
            )
        else:
            logging.info("Restreamer is disabled.")
            self.restreamer = None

    def start(self):
        try:
            logging.info("Starting motion detector...")

            if self.object_detector is not None:
                logging.info("Initializing object detector...")
                self.object_detector.initialize()
                logging.info("Object detector initialized successfully.")
            else:
                logging.warning(
                    "Object detector is not configured, skipping initialization."
                )

            if self.restreamer is not None:
                logging.info("Starting FFmpeg subprocess for RTSP output...")
                self.restreamer.spawn_ffmpeg_subprocess()
            else:
                logging.info(
                    "Restreamer is not configured, skipping FFmpeg subprocess."
                )

            logging.info("Starting video streamer...")
            self.video_streamer.start()
            logging.info("Video streamer started successfully.")
        except KeyboardInterrupt:
            logging.info("Interrupted by user, shutting down...")
        except Exception as e:
            logging.error(f"An error occurred: {e}")
        finally:
            self.stop()

    def stop(self):
        try:
            logging.info("Shutting down motion detection...")
            self.video_streamer.stop()
            if self.kafka_producer is not None:
                self.kafka_producer.flush()
                self.kafka_producer.close()
            if self.restreamer is not None:
                self.restreamer.close()
        except Exception as e:
            logging.error(f"Error during shutdown: {e}")

    def on_frame(self, frame):
        detection_frame = cv2.cvtColor(
            cv2.resize(
                frame,
                self.detector_frame_size,
            ),
            cv2.COLOR_BGR2GRAY,
        )
        detections = self.background_subtractor.get_detections(detection_frame)

        for det in detections:
            x1, y1, x2, y2 = det
            cv2.rectangle(detection_frame, (x1, y1), (x2, y2), (0, 255, 0), 3)

        if detections.size > 0:
            logging.info(f"Detected {len(detections)} objects in the frame.")
            self.send_frame_to_kafka(frame=detection_frame)

            if self.restreamer is not None:
                self.restreamer.write_frame(detection_frame)

    def send_frame_to_kafka(self, frame):
        """
        Encodes the frame as JPEG and sends it to Kafka with appropriate headers.
        """
        if self.kafka_producer and self.kafka_topic:
            ret, buffer = cv2.imencode(".jpg", frame)
            if ret:
                future = self.kafka_producer.send(
                    self.kafka_topic,
                    value=buffer.tobytes(),
                    key=self.camera_id.encode("utf-8"),
                    headers=[
                        ("timestamp", str(time.time()).encode("utf-8")),
                        ("encoding", b"jpg"),
                    ],
                )
                future.add_callback(
                    lambda record_metadata: logging.debug(
                        f"Frame sent successfully: {record_metadata}"
                    )
                )
                future.add_errback(
                    lambda exc: logging.debug(f"Failed to send frame: {exc}")
                )
        else:
            logging.warning("Kafka producer or topic not set, skipping Kafka send.")
