import logging
import subprocess


class FfmpegReStreamerService:
    def __init__(self, stream_name, frame_size, fps = 10):
        self.stream_name = stream_name
        self.width = frame_size[0]
        self.height = frame_size[1]
        self.fps = fps
        self.ffmpeg_proc = None

    def spawn_ffmpeg_subprocess(self):
        """
        Starts the FFmpeg subprocess for RTSP output.
        """
        self.ffmpeg_proc = subprocess.Popen(
            [
                "ffmpeg",
                "-y",
                "-f",
                "rawvideo",
                "-vcodec",
                "rawvideo",
                "-pix_fmt",
                # "bgr24",
                "gray",  # Use 'gray' for grayscale processing
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
                f"rtsp://127.0.0.1:8554/{self.stream_name}",  # Change to your RTSP server URL
            ],
            stdin=subprocess.PIPE,
        )

    def write_frame(self, frame):
        """
        Writes a single frame to the FFmpeg subprocess.
        """
        expected_shape = (self.height, self.width)
        if frame.shape != expected_shape:
            logging.error(
                f"Frame shape mismatch: expected {expected_shape}, got {frame.shape}"
            )
            return
        if self.ffmpeg_proc and self.ffmpeg_proc.stdin:
            try:
                self.ffmpeg_proc.stdin.write(frame.tobytes())
            except Exception as e:
                logging.error(f"Failed to write frame to FFmpeg subprocess: {e}")

    def close(self):
        """
        Closes the FFmpeg subprocess.
        """
        if self.ffmpeg_proc:
            try:
                self.ffmpeg_proc.stdin.close()
                self.ffmpeg_proc.wait()
                logging.info("FFmpeg subprocess closed successfully.")
            except Exception as e:
                logging.error(f"Failed to close FFmpeg subprocess: {e}")
