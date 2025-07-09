 
import logging 
import threading
import queue
import numpy as np
import cv2
import time 


class VideoRecorderService:

    def __init__(
        self,
        storage_dir: str,
        fps: int,
        frame_size: tuple[int, int],
        chunk_gap_seconds: int = 5 * 60,  # Default to 5 minutes
    ):
        self.fps = fps
        self.frame_size = frame_size
        self.storage_dir = storage_dir
        self.chunk_gap_seconds = chunk_gap_seconds

        self.video_writer = None
        self.prev_timestamp = None
        self.frame_queue = queue.Queue(maxsize=100)
        self.stop_event = threading.Event()
        self.worker_thread = threading.Thread(target=self._worker, daemon=True)
        
    def start(self) -> None:
        logging.info("Starting worker thread for frame processing...")
        self.worker_thread.start()

    def stop(self) -> None: 
        logging.info("Stopping video recorder service...")
        self.stop_event.set()
        self.worker_thread.join()
        if self.video_writer is not None:
            self.video_writer.release()
            self.video_writer = None
            logging.info("Released video writer.")

    def write_frame(
            self,
            frame: cv2.UMat,
            detections: np.array,
            detection_frame_size: tuple[int, int],
        ) -> None:
            # Put frame data into the queue for the worker thread
            try:
                if(self.worker_thread.is_alive() is False):
                    logging.error("VideoRecorderService Worker thread is not alive. Cannot write frame.")
                    return
                
                self.frame_queue.put_nowait((frame.copy(), detections.copy(), detection_frame_size))
            except queue.Full:
                logging.error("Frame queue is full. Dropping frame.")

    def _worker(self):
        while not self.stop_event.is_set():
            try:
                frame, detections, detection_frame_size = self.frame_queue.get(timeout=1)
                self._write(frame, detections, detection_frame_size)
            except queue.Empty:
                time.sleep(0.1)  # Sleep briefly to avoid busy waiting
                continue

    def _write(
        self,
        original_frame: cv2.UMat,
        detections: np.array,
        detection_frame_size: tuple[int, int],
    ) -> None:
        try:  
            record_frame = cv2.resize(original_frame, self.frame_size, interpolation=cv2.INTER_LINEAR) 
            timestamp = time.time()
            self.paint_overlays(
                frame=record_frame,
                timestamp=timestamp,
                detections=detections,
                detection_frame_size=detection_frame_size,
            )

            # Check if we need to start a new chunk
            start_new_chunk = False
            if self.video_writer is None:
                start_new_chunk = True
            elif (
                self.prev_timestamp is not None
                and (timestamp - self.prev_timestamp) >= self.chunk_gap_seconds
            ):
                # Close previous chunk
                self.video_writer.release()
                self.video_writer = None
                logging.info("Closed video chunk due to timestamp gap.")
                start_new_chunk = True

            if start_new_chunk: 
                chunk_filename = self.get_video_path(timestamp, "avi")
                fourcc = cv2.VideoWriter_fourcc(
                    *"XVID"
                )  # Or HEVC, but ffmpeg needs to support it
                self.video_writer = cv2.VideoWriter(
                    chunk_filename, fourcc, self.fps, self.frame_size
                )
                logging.info(f"Started new video chunk: {chunk_filename}")

            self.video_writer.write(record_frame)
            self.prev_timestamp = timestamp
            logging.debug("Frame written to video chunk.")
        except Exception as e:
            logging.error(f"Error while recording frame: {e}")

    def get_video_path(self, timestamp: float, extension: str) -> str:
       return f"{self.storage_dir}/video/{self.get_filename(timestamp, extension)}"

    def get_filename(self, timestamp: float, extension: str) -> str:
        timestamp_str = time.strftime("%Y-%m-%d_%H:%M:%S", time.localtime(timestamp))
        return f"{timestamp_str}.{extension}"

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
