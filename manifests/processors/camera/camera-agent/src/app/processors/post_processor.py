import logging 
import threading
import queue
from typing import Tuple
import numpy as np
import cv2
import time 
import env as environment
from services.video_recorder import VideoRecorderService
from services.video_restreamer import VideoRestreamerService
from services.motion_detector import MotionEvent

logger = logging.getLogger(__name__)

class PostProcessor:

    def __init__(self):
        self.event_queue = queue.Queue[MotionEvent](maxsize=100)
        self.stop_event = threading.Event()
        self.worker_thread = threading.Thread(target=self._worker, daemon=True)

        self.processor_fps = environment.postprocessor_fps
        self.processor_frame_size = environment.postprocessor_frame_size
        self.storage_dir = environment.postprocessor_recorder_storage_dir
        self.processor_restream_url = environment.postprocessor_stream_url
        self.detector_frame_size = environment.detector_frame_size

        self.video_recorder = VideoRecorderService(
            fps=self.processor_fps,
            frame_size=self.processor_frame_size,
            storage_dir=self.storage_dir,
        )

        self.video_restreamer = VideoRestreamerService(
            stream_url=self.processor_restream_url,
            frame_size=self.processor_frame_size,
            fps=self.processor_fps,
        ) 
        
    def start(self) -> None:
        logger.info("Starting worker thread for frame processing...")
        self.worker_thread.start() 
        logger.info("Worker thread started successfully.")

        if environment.postprocessor_enable_restreamer:
            logger.info("Starting video_restreamer")
            self.video_restreamer.start()
        else:
            logger.info(
                "Restreamer is not configured, skipping ... "
            )  

    def stop(self) -> None: 
        logger.info("Stopping post processor...")
        self.stop_event.set()
        self.worker_thread.join()
        if self.video_writer is not None:
            self.video_writer.release()
            self.video_writer = None 

        if environment.postprocessor_enable_restreamer and self.video_restreamer is not None:
            self.video_restreamer.stop() 

        logger.info("Post processor stopped successfully.")

    def on_motion(self, event: MotionEvent) -> None:
            # Put frame data into the queue for the worker thread
            try:
                if(self.worker_thread.is_alive() is False):
                    logger.error("Worker thread is not alive. Cannot write frame.")
                    return
                 
                self.event_queue.put_nowait(event)
            except queue.Full:
                logger.error("Frame queue is full. Dropping frame.")

    def _worker(self):
        while not self.stop_event.is_set():
            try:
                event = self.event_queue.get(timeout=1)
                self._process(event)
            except queue.Empty:
                time.sleep(0.1)  # Sleep briefly to avoid busy waiting
                continue

    def _process(self, event: MotionEvent) -> None:
        try:  
            original_frame = event.frame_event.frame
            detected_motions = event.detected_motions
            record_frame = cv2.resize(original_frame, self.processor_frame_size, interpolation=cv2.INTER_LINEAR) 
            timestamp = time.time()
            self.paint_overlays(
                frame=record_frame,
                timestamp=timestamp,
                detections=detected_motions,
                detection_frame_size=self.detector_frame_size,
            )

            self.video_recorder.write_frame(frame=record_frame, timestamp=timestamp)

            if environment.postprocessor_enable_restreamer:
                self.video_restreamer.write_frame(
                    frame=record_frame,
                    timestamp=timestamp,
                )
        except Exception as e:
            logger.error(f"Error while processing frame: {e}")
 
    def paint_overlays(
        self,
        frame: cv2.UMat,
        timestamp: float,
        detections: np.array,
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
  