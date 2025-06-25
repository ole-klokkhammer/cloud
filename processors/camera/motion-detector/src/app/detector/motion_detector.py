import logging
import uuid
import cv2
import env as environment
import time
import os
import pandas as pd
from datetime import datetime


class MotionDetector:
    def __init__(self, stream_url, kafka_producer=None, kafka_topic=None):
        self.stream_url = stream_url
        self.kafka_producer = kafka_producer
        self.kafka_topic = kafka_topic
        self.camera_id = stream_url 

        self.failures = 0
        self.max_failures = 10

        self.motion_threshold = 500
        self.recording = False
        self.frame_number = 0
        self.recording_id = None
        self.min_record_time = 3  # seconds

        self.reference_frame = None
        self.last_motion_time = None
        self.video = None

    def run(self):
        try:
            os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = (
                "rtsp_transport;tcp|stimeout;60000"
            )
            self.video = cv2.VideoCapture(self.stream_url)
            time.sleep(2)  # Allow time for the stream to stabilize

            fps = self.video.get(cv2.CAP_PROP_FPS) or 20.0
            width = int(self.video.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(self.video.get(cv2.CAP_PROP_FRAME_HEIGHT))

            while True:
                check, frame = self.video.read()
                if not self.handle_stream_failure(check, self.video):
                    continue

                simplified_frame = self.simplify_frame(frame)
                if self.reference_frame is None:
                    self.reference_frame = simplified_frame
                    continue  # skip the first frame

                motion_detected = self.detect_motion(
                    reference_frame=self.reference_frame,
                    simplified_frame=simplified_frame,
                    threshold=self.motion_threshold,
                )

                if motion_detected:
                    self.last_motion_time = time.time()
                    self.reference_frame = simplified_frame
                    if self.recording is False:
                        self.frame_number = 0
                        self.recording_id = uuid.uuid4()
                        self.recording = True
                else:
                    if self.last_motion_time is not None and (
                        time.time() - self.last_motion_time > self.min_record_time
                    ):
                        self.recording = False
                        self.recording_id = None
                        self.frame_number = 0

                if self.recording is True:
                    if self.kafka_producer and self.kafka_topic:
                        ret, buffer = cv2.imencode(".jpg", frame)
                        if ret:
                            self.kafka_producer.send(
                                self.kafka_topic,
                                value=buffer.tobytes(),
                                key=self.camera_id.encode("utf-8"),
                                headers=[
                                    ("recording_id", str(self.recording_id).encode("utf-8")),
                                    ("frame_number", str(self.frame_number).encode("utf-8")),
                                    ("timestamp", str(time.time()).encode("utf-8")),
                                    ("fps", str(fps).encode("utf-8")),
                                    ("width", str(width).encode("utf-8")),
                                    ("height", str(height).encode("utf-8")),
                                    ("encoding", b"jpg"),
                                ],
                            )
                            self.frame_number += 1
                    else:
                        logging.warning(
                            "Kafka producer or topic not set, skipping Kafka send."
                        )

        except KeyboardInterrupt:
            logging.info("Interrupted by user, shutting down...")
        finally:
            if self.video is not None:
                self.video.release()
                logging.info("Video capture released.")

    def handle_stream_failure(self, check, video):
        """
        Handles video stream read failures and attempts reconnection if needed.
        Returns True if the stream is OK, False if it should continue to next loop.
        """
        if not check:
            self.failures += 1
            logging.warning(
                f"Failed to read from stream ({self.failures}/{self.max_failures})"
            )
            if self.failures >= self.max_failures:
                logging.error("Max failures reached, attempting to reconnect...")
                video.release()
                logging.info("Waiting for 2 seconds before reconnecting...")
                time.sleep(2)
                self.video = cv2.VideoCapture(self.stream_url)
                self.failures = 0
            return False
        else:
            self.failures = 0
            return True

    def simplify_frame(self, frame):
        """
        Converts frame to grayscale and applies Gaussian blur.
        Returns the simplified frame.
        """
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        simplified_frame = cv2.GaussianBlur(gray_frame, (21, 21), 0)
        return simplified_frame

    def detect_motion(self, reference_frame, simplified_frame, threshold) -> bool:
        """
        Checks contours for motion above the threshold.
        Sets self.motion and self.last_motion_time if motion is detected.
        """
        contours = self.get_contours(reference_frame, simplified_frame)
        motion = False
        for contour in contours:
            area = cv2.contourArea(contour)
            if area < threshold:
                continue
            motion = True
            break
        return motion

    def get_contours(self, reference_frame, simplified_frame):
        """
        Computes contours of moving objects between reference and current frame.
        """
        diff_frame = cv2.absdiff(reference_frame, simplified_frame)
        _, thresh_frame = cv2.threshold(diff_frame, 50, 255, cv2.THRESH_BINARY)
        thresh_frame = cv2.dilate(thresh_frame, None, iterations=2)
        contours, _ = cv2.findContours(
            thresh_frame.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )
        return contours
