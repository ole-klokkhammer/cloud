import logging
import subprocess
import threading
import queue
import time
import cv2
import numpy as np

class VideoRestreamerService:
    def __init__(self, stream_url, frame_size, fps):
        self.stream_url = stream_url
        self.width = frame_size[0]
        self.height = frame_size[1]
        self.fps = fps
        self.ffmpeg_proc = None

        self.frame_queue = queue.Queue(maxsize=100)
        self.stop_event = threading.Event()
        self.worker_thread = threading.Thread(target=self._worker, daemon=True)

    def start(self): 
        try:
            logging.info("Starting video streamer service...")
            logging.info(f"Stream name: {self.stream_url}, Frame size: {self.width}x{self.height}, FPS: {self.fps}")
            self.ffmpeg_proc = subprocess.Popen(
            [
                "ffmpeg",
                "-y",
                "-f",
                "rawvideo",
                "-vcodec",
                "rawvideo",
                "-pix_fmt",
                "gray",
                # "bgr24", 
                "-s",
                f"{self.width}x{self.height}",
                "-r",
                str(self.fps),
                "-i",
                "-",  # Input from stdin
                "-c:v",
                "libx264",
                "-preset",
                "ultrafast",
                "-tune",
                "zerolatency",
                "-f",
                "rtsp",
                f"{self.stream_url}", 
            ],
                stdin=subprocess.PIPE,
            )
            self.worker_thread.start()
        except Exception as e:
            logging.error(f"Failed to start FFmpeg subprocess: {e}")
            self.ffmpeg_proc = None
            return

    def stop(self): 
        logging.info("Stopping FFmpeg restreamer service...")
        self.stop_event.set()
        self.worker_thread.join()
        if self.ffmpeg_proc:
            try:
                self.ffmpeg_proc.stdin.close()
                self.ffmpeg_proc.wait()
                logging.info("FFmpeg subprocess closed successfully.")
            except Exception as e:
                logging.error(f"Failed to close FFmpeg subprocess: {e}")

    def write_frame(
            self,
            frame: cv2.UMat,
            detections: np.array,
            detection_frame_size: tuple[int, int],
        ) -> None:
            # Put frame data into the queue for the worker thread
            try:
                if(self.worker_thread.is_alive() is False):
                    logging.error("VideoRestreamerService Worker thread is not alive. Cannot write frame.")
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
    ): 
        try:  
            frame = cv2.resize(original_frame, (self.width, self.height), interpolation=cv2.INTER_LINEAR) 
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)  # Convert to grayscale
            timestamp = time.time()
            self.paint_overlays(
                frame=frame,
                timestamp=timestamp,
                detections=detections,
                detection_frame_size=detection_frame_size,
            )
            if self.ffmpeg_proc and self.ffmpeg_proc.stdin:
                try:
                    self.ffmpeg_proc.stdin.write(frame.tobytes())
                except Exception as e:
                    logging.error(f"Failed to write frame to FFmpeg subprocess: {e}")
        except Exception as e:
            logging.error(f"Error while recording frame: {e}")


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
