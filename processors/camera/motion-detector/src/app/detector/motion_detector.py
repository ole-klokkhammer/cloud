import logging
import signal
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
        self.kafka_frame_number = -1
        self.recording_id = None
        self.min_record_time = 3  # seconds
        self.target_fps = 20.0
        self.frame_interval = 1.0 / self.target_fps

        # TARGET_FPS = 10
        # FRAME_INTERVAL = 1.0 / TARGET_FPS

        # while True:
        #     start_time = time.time()
        #     # ... existing code ...
        #     elapsed = time.time() - start_time
        #     if elapsed < FRAME_INTERVAL:
        #         time.sleep(FRAME_INTERVAL - elapsed)

        self.reference_frame = None
        self.last_motion_time = None
        self.video = None

    def shutdown(self, signum=None, frame=None):
        logging.info("Shutting down motion detection...")
        if self.kafka_producer is not None:
            self.kafka_producer.flush()
            self.kafka_producer.close()
            exit(0)

    def run(self):
        try:
            logging.info("Running motion detection...")

            # Register signal handlers
            signal.signal(signal.SIGINT, self.shutdown)
            signal.signal(signal.SIGTERM, self.shutdown)

            os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = (
                "rtsp_transport;tcp|stimeout;60000"
            )
            self.video = cv2.VideoCapture(self.stream_url)
            time.sleep(2)  # Allow time for the stream to stabilize

            fps = self.video.get(cv2.CAP_PROP_FPS) or 20.0
            width = int(self.video.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(self.video.get(cv2.CAP_PROP_FRAME_HEIGHT))

            logging.info(
                f"Stream properties - FPS: {fps}, Width: {width}, Height: {height}"
            )

            while True:

                start_time = time.time()  # Start timing

                check, frame = self.video.read()

                if not self.handle_stream_failure(check):
                    continue

                simplified_frame = self.simplify_frame(frame)
                if self.reference_frame is None:
                    self.reference_frame = simplified_frame
                    if environment.LOCAL_DEBUG:
                        logging.info(
                            "Reference frame initialized, saving to disk for debugging."
                        )
                        cv2.imwrite(
                            "../snapshots/reference_frame.jpg", self.reference_frame
                        )
                        cv2.imwrite(
                            "../snapshots/simplified_frame.jpg", simplified_frame
                        )
                    continue  # skip the first frame

                motion_detected = self.detect_motion(
                    reference_frame=self.reference_frame,
                    simplified_frame=simplified_frame,
                    threshold=self.motion_threshold,
                )
                end_time = time.time()
                frame_time = end_time - start_time
                logging.debug(f"Computation time for frame: {frame_time:.4f} seconds")

                if motion_detected:
                    self.last_motion_time = time.time()
                    self.reference_frame = simplified_frame
                    if self.recording is False:
                        self.start_recording()
                elif self.recording and self.last_motion_time is not None:
                    # Check if enough time has passed since the last motion
                    time_since_last_motion = time.time() - self.last_motion_time
                    time_left = max(0, self.min_record_time - time_since_last_motion)
                    logging.info(
                        f"No motion detected, stopping recording in {time_left:.2f} seconds."
                    )
                    if time_since_last_motion > self.min_record_time:
                        self.stop_recording()

                if self.recording is True:
                    logging.info(
                        "Recording: recording_id=%s, frame_number=%s",
                        self.recording_id,
                        self.kafka_frame_number,
                    )
                    self.kafka_frame_number += 1
                    self.send_frame_to_kafka(
                        topic=self.kafka_topic,
                        frame_number=self.kafka_frame_number,
                        recording_id=self.recording_id,
                        frame=frame,
                        fps=fps,
                        width=width,
                        height=height,
                    ) 

        except KeyboardInterrupt:
            logging.info("Interrupted by user, shutting down...")
        finally:
            if self.video is not None:
                self.video.release()
                logging.info("Video capture released.")

    def start_recording(self):
        """
        Starts recording by setting the recording flag to True.
        This method can be called externally to start recording.
        """
        self.recording = True
        self.recording_id = uuid.uuid4()
        self.kafka_frame_number = -1
        logging.info("Recording started with ID: %s", self.recording_id)

    def stop_recording(self):
        """
        Stops recording by setting the recording flag to False.
        This method can be called externally to stop recording.
        """
        self.recording = False
        self.recording_id = None
        self.kafka_frame_number = 0
        logging.info("Recording stopped.")

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

    def handle_stream_failure(self, check):
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
                if self.video is not None:
                    self.video.release()
                logging.info("Waiting for 2 seconds before reconnecting...")
                time.sleep(2)
                self.video = cv2.VideoCapture(self.stream_url)
                self.failures = 0
            return False
        else:
            self.failures = 0
            return True

    def simplify_frame(self, frame, size=(640, 480), blur_kernel=(5, 5)):
        """
        Converts frame to a lower resolution, grayscale, and applies Gaussian blur.
        Returns the simplified frame to be used in motion detection.

        Args:
            frame (np.ndarray): The input frame.
            size (tuple): The target size for resizing (width, height).
            blur_kernel (tuple): The kernel size for Gaussian blur.

        Returns:
            np.ndarray: The processed frame.
        """
        return cv2.GaussianBlur(
            cv2.cvtColor(cv2.resize(frame, size), cv2.COLOR_BGR2GRAY), blur_kernel, 0
        )

    def detect_motion(self, reference_frame, simplified_frame, threshold) -> bool:
        """
        Checks contours for motion above the threshold.
        Sets self.motion and self.last_motion_time if motion is detected.
        """
        # self.start_time = time.time()
        contours = self.get_contours(reference_frame, simplified_frame)
        # encode_time = time.time() - self.start_time
        # logging.info(f"motion detect time: {encode_time:.4f} seconds")
        motion = False
        for contour in contours:
            area = cv2.contourArea(contour)
            logging.debug(f"Contour area: {area}")
            if area < threshold:
                continue
            motion = True
            break
        return motion

    def get_contours(
        self,
        reference_frame,
        simplified_frame,
        # threshold_value Good for most indoor scenes; increase if you get too many false positives
        threshold_value=20,
        # dilate_iterations 1-3 is typical; higher fills gaps but can merge small objects
        dilate_iterations=2,
        # morph_kernel_size (3, 3) or (5, 5) are common; larger removes more noise but can erase small motion
        morph_kernel_size=(3, 3),
        # use_morph_open True helps remove small noise; set False if you want to keep all small changes
        use_morph_open=True,
    ):
        """
        Computes contours of moving objects between reference and current frame.

        Args:
            reference_frame (np.ndarray): The reference grayscale frame.
            simplified_frame (np.ndarray): The current grayscale frame.
            threshold_value (int): Threshold for binarization.
            dilate_iterations (int): Number of dilation iterations.
            morph_kernel_size (tuple): Kernel size for morphological operations.
            use_morph_open (bool): Whether to apply morphological opening to remove noise.

        Returns:
            list: List of detected contours.
        """
        diff_frame = cv2.absdiff(reference_frame, simplified_frame)
        _, thresh_frame = cv2.threshold(
            diff_frame, threshold_value, 255, cv2.THRESH_BINARY
        )
        if use_morph_open:
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, morph_kernel_size)
            thresh_frame = cv2.morphologyEx(thresh_frame, cv2.MORPH_OPEN, kernel)
        thresh_frame = cv2.dilate(thresh_frame, None, iterations=dilate_iterations)
        contours, _ = cv2.findContours(
            thresh_frame, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )
        return contours
