import asyncio
import logging
import os
import queue
import threading
from typing import Optional, Protocol

import numpy as np
import cv2
import time
from dataclasses import dataclass


@dataclass
class MotionData:
    detected_motions: np.ndarray = np.empty((0, 6), dtype=np.float32)
    detected_objects: np.ndarray = np.empty((0, 6), dtype=np.float32)


@dataclass
class FrameEvent:
    frame: cv2.UMat
    frame_size: tuple[int, int]
    timestamp: float
    fps: int
    motion: MotionData


class OnFrameCallback(Protocol):
    def __call__(self, event: FrameEvent):
        None


logger = logging.getLogger(__name__)


# https://github.com/itberrios/CV_projects/blob/main/motion_detection/motion_detection_utils.py
class StreamProcessor:
    def __init__(self, stream_url: str):
        self.enhancers: list[OnFrameCallback] = []
        self.post_processor: Optional[OnFrameCallback] = None
        self.stream_url = stream_url

        self.video = None
        self.failures = 0
        self.max_failures = 10

        self.stop_event = asyncio.Event()
        self.capture_loop_stopped_event = asyncio.Event()
        self.process_loop_stopped_event = asyncio.Event()
        self.frame_queue: asyncio.Queue[FrameEvent] = asyncio.Queue(maxsize=100)

    async def start(self):
        self.stop_event.clear()
        self.capture_loop_stopped_event.clear()
        self.process_loop_stopped_event.clear()
        self.video = cv2.VideoCapture(self.stream_url)
        await asyncio.gather(self._capture_loop(), self._process_loop())

    async def stop(self):
        self.stop_event.set()
        await self.capture_loop_stopped_event.wait()
        await self.process_loop_stopped_event.wait()
        if self.video:
            await asyncio.to_thread(self.video.release)
            self.video = None

    async def _capture_loop(self):
        logger.info(f"Initializing video stream from {self.stream_url}...")
        os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = (
            "rtsp_transport;tcp|stimeout;60000"
        )
        self.video = cv2.VideoCapture(self.stream_url)
        await asyncio.sleep(2)

        if not self.video.isOpened():
            raise Exception(f"Failed to open video stream: {self.stream_url}")

        logger.info("Video stream initialized successfully.")
        while not self.stop_event.is_set():
            check, frame = await asyncio.to_thread(self.video.read)
            if not self.handle_stream_failure(check):
                await asyncio.sleep(1)
                continue

            event = FrameEvent(
                frame=frame,
                fps=10,  # int(self.video.get(cv2.CAP_PROP_FPS))
                frame_size=(
                    int(self.video.get(cv2.CAP_PROP_FRAME_WIDTH)),
                    int(self.video.get(cv2.CAP_PROP_FRAME_HEIGHT)),
                ),
                timestamp=time.time(),
                motion=MotionData(),
            )
            try:
                self.frame_queue.put_nowait(event)
            except asyncio.QueueFull:
                await self.frame_queue.get()  # remove oldest frame if queue is full
                await self.frame_queue.put(event)

        self.capture_loop_stopped_event.set()

    async def _process_loop(self):
        while not self.stop_event.is_set():
            try:

                event = await self.frame_queue.get()

                start_time = time.time()
                for enhancer in self.enhancers:
                    enhancer(event)
                if self.post_processor:
                    self.post_processor(event)
                end_time = time.time()

                processing_time = end_time - start_time
                logger.debug(
                    f"Processed frame in {processing_time:.4f} seconds, FPS: {1 / processing_time:.2f}"
                )
            except Exception as e:
                logger.error(f"Processing error: {e}")

        self.process_loop_stopped_event.set()

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

    def add_enhancer(self, enhancer: OnFrameCallback):
        """Register a callback to be called on output events."""
        self.enhancers.append(enhancer)
        return self  # Enable chaining

    def set_post_processor(self, post_processor: OnFrameCallback):
        self.post_processor = post_processor
        return self
