#!/usr/bin/python3

from dataclasses import dataclass
import os
import logging
import signal
import time
from typing import TypedDict
import cv2
import env as environment
from services.restreamer import FfmpegReStreamer
from services.object_detector import CoralTPUObjectDetector
from services.bg_subtractor_mog2 import BackgroundSubtractorMOG2
from services.video_streamer import VideoStreamer
from kafka import KafkaProducer


@dataclass
class ObjectDetectorConfig:
    model_file: str
    label_file: str


@dataclass
class RestreamerConfig:
    stream_name: str
    frame_size: tuple
    fps: int


@dataclass
class CameraConfig:
    stream_url: str
    camera_id: str


@dataclass
class KafkaConfig:
    bootstrap_servers: str
    topic: str


@dataclass
class MotionDetectorConfig:
    frame_width: int
    frame_height: int


class MotionDetector:
    def __init__(
        self,
        camera_config: CameraConfig,
        motion_detector_config: MotionDetectorConfig,
        object_detector_config: ObjectDetectorConfig | None = None,
        restreamer_config: RestreamerConfig | None = None,
        kafka_config: KafkaConfig | None = None,
    ):
        self.motion_detector_config = motion_detector_config
        self.camera_config = camera_config
        self.restreamer_config = restreamer_config
        self.object_detector_config = object_detector_config
        self.kafka_config = kafka_config

    def initialize(self):
        self.video_streamer = VideoStreamer(
            stream_url=environment.entrance_roof_stream_url, on_frame=self.on_frame
        )

        self.background_subtractor = BackgroundSubtractorMOG2(
            history=100, varThreshold=5, detectShadows=True, shadowThreshold=0.5
        )

        self.object_detector = None
        if self.object_detector_config is not None:
            self.object_detector = CoralTPUObjectDetector(
                model_file=self.object_detector_config.model_file,
                label_file=self.object_detector_config.label_file,
            )
        else:
            logging.warning(
                "Object detector is not configured, skipping initialization."
            )

        self.restreamer = None
        if self.restreamer_config is not None:
            self.restreamer = FfmpegReStreamer(
                stream_name=self.restreamer_config.stream_name,
                frame_size=self.restreamer_config.frame_size,
                fps=self.restreamer_config.fps,
            )
        else:
            logging.warning("Restreamer is not configured, skipping initialization.")

        self.kafka_producer = None
        if self.kafka_config is not None:
            self.kafka_topic = self.kafka_config.topic
            self.kafka_producer = KafkaProducer(
                bootstrap_servers=self.kafka_config.bootstrap_servers,
                value_serializer=lambda v: v,  # Send bytes
            )
        else:
            logging.warning(
                "Kafka configuration is not set, skipping Kafka producer initialization."
            )

    def start(self):
        try:
            logging.info("Starting motion detector...")

            logging.info("Initializing parts needed for motion detection...")
            self.initialize()
            logging.info("Motion detector initialized successfully.")

            if self.object_detector is not None:
                logging.info("Initializing object_detector...")
                self.object_detector.initialize()
                logging.info("Object detector initialized successfully.")
            else:
                logging.info("Object detector is not configured, skipping initialization.")
 
            if self.restreamer is not None:
                logging.info("Starting FFmpeg subprocess for RTSP output...")
                self.restreamer.spawn_ffmpeg_subprocess()
            else:
                logging.info("Restreamer is not configured, skipping FFmpeg subprocess.")   


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
        start_time = time.time()

        detector_frame_width = self.motion_detector_config.frame_height 
        detector_frame_height = self.motion_detector_config.frame_width
        detection_frame = cv2.cvtColor(
            cv2.resize(
                frame,
                (
                    detector_frame_width,
                    detector_frame_height,
                ),
            ),
            cv2.COLOR_BGR2GRAY,
        )
        detections = self.background_subtractor.get_detections(detection_frame)

        for det in detections:
            x1, y1, x2, y2 = det
            cv2.rectangle(detection_frame, (x1, y1), (x2, y2), (0, 255, 0), 3)

        if detections.size > 0:
            logging.info(f"Detected {len(detections)} objects in the frame.")
            if self.restreamer is not None:
                self.restreamer.write_frame(detection_frame)

            if self.kafka_producer is not None:
                self.send_frame_to_kafka(
                    self.kafka_topic,
                    frame=detection_frame,
                    width=detector_frame_width,
                    height=detector_frame_height,
                )

        end_time = time.time()
        processing_time = end_time - start_time
        # logging.info(f"Frame processing time: {processing_time:.4f} seconds")

    def send_frame_to_kafka(self, topic, frame, width, height):
        """
        Encodes the frame as JPEG and sends it to Kafka with appropriate headers.
        """
        if self.kafka_producer and self.kafka_topic:
            ret, buffer = cv2.imencode(".jpg", frame)
            if ret:
                future = self.kafka_producer.send(
                    topic,
                    value=buffer.tobytes(),
                    key=self.camera_config.camera_id.encode("utf-8"),
                    headers=[
                        ("timestamp", str(time.time()).encode("utf-8")),
                        ("width", str(width).encode("utf-8")),
                        ("height", str(height).encode("utf-8")),
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
