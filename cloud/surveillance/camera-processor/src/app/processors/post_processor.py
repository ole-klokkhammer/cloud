import logging
from typing import Tuple
import numpy as np
import cv2
import time
from services.video_recorder import VideoRecorderService
from app.processors.stream_processor import FrameEvent

logger = logging.getLogger(__name__)


class PostProcessor:

    def __init__(
        self,
        fps: int,
        frame_size: Tuple[int, int],
        storage_dir: str,
        detector_frame_size: Tuple[int, int],
    ):
        self.processor_fps = fps
        self.processor_frame_size = frame_size
        self.storage_dir = storage_dir
        self.detector_frame_size = detector_frame_size

        self.video_recorder = VideoRecorderService(
            fps=self.processor_fps,
            frame_size=self.processor_frame_size,
            storage_dir=self.storage_dir,
        )

        self.frame_count = 0
        self.fps_start_time = time.time()

    def stop(self) -> None:
        logger.info("Stopping post processor...")
        if self.video_writer is not None:
            self.video_writer.release()
            self.video_writer = None

        logger.info("Post processor stopped successfully.")

    def process(self, event: FrameEvent) -> None:
        try:
            if event.motion.detected_motions.size > 0:
                logger.debug(
                    f"Detected {event.motion.detected_motions.shape[0]} motions in frame."
                )

                timestamp = event.timestamp
                original_frame = event.frame
                detected_motions = event.motion.detected_motions
                detected_objects = event.motion.detected_objects

                record_frame = cv2.resize(
                    original_frame,
                    self.processor_frame_size,
                    interpolation=cv2.INTER_LINEAR,
                )
                self.paint_overlays(
                    frame=record_frame,
                    timestamp=timestamp,
                    detections=detected_motions,
                    detection_frame_size=self.detector_frame_size,
                )
                self.video_recorder.write_frame(frame=record_frame, timestamp=timestamp)

        except Exception as e:
            logger.error(f"Error while processing frame: {e}")

    def paint_overlays(
        self,
        frame: cv2.UMat,
        timestamp: float,
        detections: np.ndarray,
        detection_frame_size: tuple[int, int],
    ) -> None:
        frame_height, frame_width = frame.shape[:2]
        det_width, det_height = detection_frame_size
        scale_x = frame_width / det_width
        scale_y = frame_height / det_height

        paint_thickness = 2
        text_color = (255, 255, 255)
        detection_rect_color = (0, 255, 0)

        for det in detections:
            x1, y1, x2, y2 = det
            # Scale detection coordinates to match the frame size
            x1 = int(x1 * scale_x)
            y1 = int(y1 * scale_y)
            x2 = int(x2 * scale_x)
            y2 = int(y2 * scale_y)
            cv2.rectangle(
                frame,
                (x1, y1),
                (x2, y2),
                detection_rect_color,
                paint_thickness,
            )

        # Draw timestamp on the frame
        timestamp_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(timestamp))
        cv2.putText(
            frame,
            timestamp_str,
            (10, frame_height - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            text_color,
            paint_thickness,
            cv2.LINE_AA,
        )
