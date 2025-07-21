#!/usr/bin/python3

import asyncio
import logging
import signal
import env as environment
from services.motion_detector import MotionDetectorService
from processors.post_processor import PostProcessor
from processors.video_processor import StreamProcessor

logging.basicConfig(
    level=logging._nameToLevel[environment.log_level.upper()],
    format="%(asctime)s %(levelname)s %(message)s",
)
logger = logging.getLogger(__name__)

shutdown_event = asyncio.Event()


def shutdown(signum, frame):
    logger.info(f"Received signal {signum}, shutting down...")
    loop = asyncio.get_event_loop()
    loop.call_soon_threadsafe(shutdown_event.set)


# Register signal handlers
signal.signal(signal.SIGINT, shutdown)
signal.signal(signal.SIGTERM, shutdown)


async def main():
    logger.info("Setting up camera agent...")

    if not environment.camera_stream_url:
        logger.error("CAMERA_STREAM_URL is not set. Exiting.")
        return

    post_processor = PostProcessor(
        fps=environment.postprocessor_fps,
        frame_size=environment.postprocessor_frame_size,
        detector_frame_size=environment.detector_frame_size,
        storage_dir=environment.postprocessor_recorder_storage_dir,
        enable_restreamer=environment.postprocessor_enable_restreamer,
        restream_url=environment.postprocessor_stream_url or "",
    )

    motion_detector = MotionDetectorService(
        detector_frame_size=environment.detector_frame_size,
        enable_object_detection=environment.enable_object_detection,
        model_file=environment.object_detector_model_file,
        label_file=environment.object_detector_label_file,
    )

    video_processor = StreamProcessor(stream_url=environment.camera_stream_url)
    video_processor.add_enhancer(motion_detector.process)
    video_processor.set_post_processor(post_processor.process)

    async def startup():
        logger.info("Starting video processor...")
        post_processor.start()
        await video_processor.start()
        logger.info("Video processor startup complete.")

    async def shutdown():
        logger.info("Shutting down video processor...")
        await video_processor.stop()
        post_processor.stop()
        logger.info("Video processor shutdown complete.")

    try:
        await startup()
        await shutdown_event.wait()
        await shutdown()
    except Exception as e:
        logger.error(f"Unhandled exception: {e}")
        await shutdown()
        raise


if __name__ == "__main__":
    asyncio.run(main())
