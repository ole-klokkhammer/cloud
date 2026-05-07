import asyncio
import logging
import os
from typing import Optional
import time
from types.frame import OnFrameCallback, FrameEvent, MotionData
import cv2

logger = logging.getLogger(__name__)


# https://github.com/itberrios/CV_projects/blob/main/motion_detection/motion_detection_utils.py
class StreamProcessor:
    def __init__(self, stream_url: str):
        self.frame_callback: Optional[OnFrameCallback] = None
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
        await asyncio.gather(self.capture_loop(), self.process_loop())

    async def stop(self):
        self.stop_event.set()
        await self.capture_loop_stopped_event.wait()
        await self.process_loop_stopped_event.wait()
        if self.video:
            await asyncio.to_thread(self.video.release)
            self.video = None

    async def capture_loop(self):
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

    async def process_loop(self):
        while not self.stop_event.is_set():
            try:
                event = await self.frame_queue.get()
                if self.frame_callback:
                    self.frame_callback(event)
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

    def set_frame_callback(self, frame_callback: OnFrameCallback):
        self.frame_callback = frame_callback
        return self
