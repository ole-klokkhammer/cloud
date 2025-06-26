#!/usr/bin/python3

import os
import logging
import signal
import time
import cv2
import env as environment
from services.restreamer import FfmpegReStreamer
from services.object_detector import CoralTPUObjectDetector
from services.bg_subtractor_mog2 import BackgroundSubtractorMOG2
from services.video_streamer import VideoStreamer
from kafka import KafkaProducer


class MotionDetector:
    def __init__(self):
        self.stream_url = environment.entrance_roof_stream_url
        self.kafka_topic = environment.kafka_topic

        self.video = None
        self.camera_id = self.stream_url
        self.detection_frame_size = (640, 480)
        self.detection_fps = 10

        self.video_streamer = VideoStreamer(
            stream_url=environment.entrance_roof_stream_url, on_frame=self.on_frame
        )

        self.background_subtractor = BackgroundSubtractorMOG2(
            history=100, varThreshold=5, detectShadows=True, shadowThreshold=0.5
        )

        self.object_detector = CoralTPUObjectDetector(
            model_file="mobilenet_ssd_v2_coco_quant_postprocess_edgetpu.tflite",
            label_file="coco_labels.txt",
        )

        self.restreamer = None
        if environment.LOCAL_DEBUG:
            self.restreamer = FfmpegReStreamer(
                stream_name="motion_detection",
                detection_frame_size=self.detection_frame_size,
                fps=self.detection_fps,
            )

        self.kafka_producer = None
        if not environment.LOCAL_DEBUG:
            self.kafka_producer = KafkaProducer(
                bootstrap_servers=environment.kafka_bootstrap_servers,
                value_serializer=lambda v: v,  # Send bytes
                max_request_size=4 * 1024 * 1024,
                compression_type=None,
                linger_ms=0,  # Send immediately
                acks=1,
            )

    def start(self):
        try:
            logging.info("Starting motion detector...")

            logging.info("Initializing object_detector...")
            self.object_detector.initialize()
            logging.info("Object detector initialized successfully.")

            # for testing purposes, we can use a re-streamer to output the processed frames
            if self.restreamer is not None:
                logging.info("Starting FFmpeg subprocess for RTSP output...")
                self.restreamer.spawn_ffmpeg_subprocess()

            logging.info("Starting video streamer...")
            self.video_streamer.start()
            logging.info("Video streamer started successfully.")
        except KeyboardInterrupt:
            logging.info("Interrupted by user, shutting down...")
        finally:
            self.video_streamer.stop()

    def stop(self):
        logging.info("Shutting down motion detection...")
        self.video_streamer.stop()
        if self.kafka_producer is not None:
            self.kafka_producer.flush()
            self.kafka_producer.close()
        if self.restreamer is not None:
            self.restreamer.close()

    def on_frame(self, frame):

        detection_frame = cv2.cvtColor(
            cv2.resize(frame, self.detection_frame_size),
            cv2.COLOR_BGR2GRAY,
        )
        detections = self.background_subtractor.get_detections(detection_frame)

        for det in detections:
            x1, y1, x2, y2 = det
            cv2.rectangle(detection_frame, (x1, y1), (x2, y2), (0, 255, 0), 3)

        if detections.size > 0:

            if self.restreamer is not None:
                self.restreamer.write_frame(detection_frame)

            # if kafka_producer is not None:
            # send_frame_to_kafka(
            #     kafka_topic,
            #     frame_number=int(time.time() * 1000),
            #     recording_id=camera_id,
            #     frame=detection_frame,
            #     fps=original_fps,
            #     width=detection_frame_size[0],
            #     height=detection_frame_size[1],
            # )

    def send_frame_to_kafka(
        self, topic, frame_number, recording_id, frame, fps, width, height
    ):
        """
        Encodes the frame as JPEG and sends it to Kafka with appropriate headers.
        """
        if self.kafka_producer and self.kafka_topic:
            ret, buffer = cv2.imencode(".jpg", frame)
            if ret:
                future = self.kafka_producer.send(
                    topic,
                    value=buffer.tobytes(),
                    key=self.camera_id.encode("utf-8"),
                    headers=[
                        ("recording_id", str(recording_id).encode("utf-8")),
                        ("frame_number", str(frame_number).encode("utf-8")),
                        ("timestamp", str(time.time()).encode("utf-8")),
                        ("fps", str(fps).encode("utf-8")),
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
