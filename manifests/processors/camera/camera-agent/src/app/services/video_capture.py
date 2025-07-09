import logging
import os
import threading
from typing import Protocol 
import cv2
import time

logger = logging.getLogger(__name__)

class OnFrameCallback(Protocol):
    def __call__(
        self, 
        frame: cv2.UMat
    ): None

# https://github.com/itberrios/CV_projects/blob/main/motion_detection/motion_detection_utils.py
class VideoCaptureService:
    def __init__(self, stream_url):
        if stream_url is None:
            raise ValueError("stream_url must not be None")
        
        self.listeners: list[OnFrameCallback] = []
        self.video = None
        self.stream_url = stream_url 
        self.failures = 0
        self.max_failures = 10

        self.running = False
        self.thread = None

    def add_listener(self, listener: OnFrameCallback):
        """Register a callback to be called on output events."""
        self.listeners.append(listener)

    def start(self):
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()

    def _run(self):
        try:
            logger.info("Initializing video stream...")
            os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = (
                "rtsp_transport;tcp|stimeout;60000"
            )
            self.video = cv2.VideoCapture(self.stream_url)
            time.sleep(2)  # Allow time for the stream to stabilize

            if not self.video.isOpened():
                raise Exception(f"Failed to open video stream: {self.stream_url}")

            original_fps = self.video.get(cv2.CAP_PROP_FPS)
            original_width = int(self.video.get(cv2.CAP_PROP_FRAME_WIDTH))
            original_height = int(self.video.get(cv2.CAP_PROP_FRAME_HEIGHT))
            logger.info("Video stream initialized successfully.")

            self.running = True
            while self.running:
                payload: tuple[bool, cv2.UMat] = self.video.read()
                check, frame = payload

                if not self.handle_stream_failure(check):
                    continue

                for on_frame in self.listeners:
                    on_frame(frame)

        except KeyboardInterrupt:
            logger.info("Interrupted by user, shutting down...")
        finally:
            if self.video is not None:
                self.video.release()
                logger.info("Video capture released.")

    def stop(self):
        try:
            logger.info("Shutting video streamer...")
            self.running = False
            if self.thread is not None:
                self.thread.join(timeout=5)
            if self.video is not None:
                self.video.release()
        except Exception as e:
            logger.error(f"Error during video streamer shutdown: {e}")

    def handle_stream_failure(self, check):
        """
        Handles video stream read failures and attempts reconnection if needed.
        Returns True if the stream is OK, False if it should continue to next loop.
        """
        if not check:
            self.failures += 1
            logger.warning(
                f"Failed to read from stream ({self.failures}/{self.max_failures})"
            )
            if self.failures >= self.max_failures:
                logger.error("Max failures reached, attempting to reconnect...")
                if self.video is not None:
                    self.video.release()
                logger.info("Waiting for 2 seconds before reconnecting...")
                time.sleep(2)
                self.video = cv2.VideoCapture(self.stream_url)
                self.failures = 0
            return False
        else:
            self.failures = 0
            return True
