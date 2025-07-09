 
import logging
from typing import Tuple  
import numpy as np
import cv2
import time 

logger = logging.getLogger(__name__)

class VideoRecorderService:

    def __init__(
        self,
        storage_dir: str,
        fps: int, 
        frame_size: Tuple[int, int],  
        chunk_gap_seconds: int = 5 * 60,  # Default to 5 minutes
    ): 
        self.fps = fps
        self.frame_size = frame_size
        self.storage_dir = storage_dir
        self.chunk_gap_seconds = chunk_gap_seconds 
        self.video_writer = None
        self.prev_timestamp = None   

    def write_frame( self, frame: cv2.UMat, timestamp: float) -> None:
        try:   
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
                logger.info("Closed video chunk due to timestamp gap.")
                start_new_chunk = True

            if start_new_chunk: 
                chunk_filename = self.get_video_path(timestamp, "avi")
                fourcc = cv2.VideoWriter_fourcc(
                    *"XVID"
                )  # Or HEVC, but ffmpeg needs to support it
                self.video_writer = cv2.VideoWriter(
                    chunk_filename, fourcc, self.fps, self.frame_size
                )
                logger.info(f"Started new video chunk: {chunk_filename}")

            self.video_writer.write(frame)
            self.prev_timestamp = timestamp
            logger.debug("Frame written to video chunk.")
        except Exception as e:
            logger.error(f"Error while writing frame: {e}")

    def get_video_path(self, timestamp: float, extension: str) -> str:
       return f"{self.storage_dir}/video/{self.get_filename(timestamp, extension)}"

    def get_filename(self, timestamp: float, extension: str) -> str:
        timestamp_str = time.strftime("%Y-%m-%d_%H:%M:%S", time.localtime(timestamp))
        return f"{timestamp_str}.{extension}"
 