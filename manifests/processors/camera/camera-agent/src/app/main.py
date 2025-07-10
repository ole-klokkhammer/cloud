#!/usr/bin/python3

import logging
import signal
import threading
import env as environment
from services.motion_detector import MotionDetectorService  
from processors.post_processor import PostProcessor
from processors.video_processor import StreamProcessor

logging.basicConfig(
    level=logging._nameToLevel[environment.log_level.upper()],
    format="%(asctime)s %(levelname)s %(message)s",
) 

logging = logging.getLogger(__name__)

if __name__ == "__main__": 
    # 3. output
    post_processor = PostProcessor()
 
    # 2. detection
    motion_detector = MotionDetectorService()  
    motion_detector.add_listener(post_processor.on_motion)

    # 1. capture
    video_processor = StreamProcessor(stream_url=environment.camera_stream_url) 
    video_processor.add_listener(motion_detector.on_frame)

    shutdown_event = threading.Event()
    def shutdown(signum, frame):
        logging.info(f"Received signal {signum}, shutting down...") 
        video_processor.stop()
        post_processor.stop()
        shutdown_event.set() 

    # Register signal handlers
    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)

    post_processor.start()
    video_processor.start() 
    shutdown_event.wait()  # Wait here until shutdown_event is set
    logging.info("Shutdown complete.")

