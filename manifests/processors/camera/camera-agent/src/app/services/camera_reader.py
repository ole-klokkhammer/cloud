import logging
import os
from typing import Callable, Optional

import numpy as np
import cv2
import time


# https://github.com/itberrios/CV_projects/blob/main/motion_detection/motion_detection_utils.py
class CameraReaderService:
    def __init__(
        self,
        stream_url,
        on_frame: Optional[Callable[[cv2.UMat], None]] = None,
    ):
        if stream_url is None:
            raise ValueError("stream_url must not be None")
        if on_frame is None:
            raise ValueError("on_frame callback must not be None")

        self.video = None
        self.stream_url = stream_url
        self.on_frame = on_frame
        self.failures = 0
        self.max_failures = 10

    def start(self):
        try:
            logging.info("Initializing video stream...")
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
            logging.info("Video stream initialized successfully.")

            while True:
                payload: tuple[bool, cv2.UMat] = self.video.read()
                check, frame = payload

                if not self.handle_stream_failure(check):
                    continue

                self.on_frame(frame)
        except KeyboardInterrupt:
            logging.info("Interrupted by user, shutting down...")
        finally:
            if self.video is not None:
                self.video.release()
                logging.info("Video capture released.")

    def stop(self):
        try:
            logging.info("Shutting video streamer...")
            if self.video is not None:
                self.video.release()
        except Exception as e:
            logging.error(f"Error during video streamer shutdown: {e}")

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
