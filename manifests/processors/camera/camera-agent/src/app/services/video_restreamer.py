import logging
import subprocess 
import cv2 

logger = logging.getLogger(__name__)

class VideoRestreamerService:
    def __init__(self, stream_url: str, frame_size: tuple[int, int], fps: int):
        self.stream_url = stream_url
        self.width = frame_size[0]
        self.height = frame_size[1]
        self.fps = fps
        self.ffmpeg_proc = None 

    def start(self): 
        try:
            logger.info("Starting video streamer service...")
            logger.info(f"Stream name: {self.stream_url}, Frame size: {self.width}x{self.height}, FPS: {self.fps}")
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
        except Exception as e:
            logger.error(f"Failed to start FFmpeg subprocess: {e}")
            self.ffmpeg_proc = None
            return

    def stop(self): 
        logger.info("Stopping FFmpeg restreamer service...") 
        if self.ffmpeg_proc:
            try:
                self.ffmpeg_proc.stdin.close()
                self.ffmpeg_proc.wait()
                logger.info("FFmpeg subprocess closed successfully.")
            except Exception as e:
                logger.error(f"Failed to close FFmpeg subprocess: {e}")

    def write_frame(
        self,
        frame: cv2.UMat,
        timestamp: float,
    ): 
        try:  
            frame = frame.copy()
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)  # Convert to grayscale 

            if self.ffmpeg_proc and self.ffmpeg_proc.stdin:
                try:
                    self.ffmpeg_proc.stdin.write(frame.tobytes())
                except Exception as e:
                    logger.error(f"Failed to write frame to FFmpeg subprocess: {e}")
        except Exception as e:
            logger.error(f"Error while restreaming frame: {e}")

 