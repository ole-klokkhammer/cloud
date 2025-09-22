import asyncio
import logging
import env as environment
from services.motion_detector import MotionDetectorService
from processors.post_processor import PostProcessor
from app.processors.stream_processor import StreamProcessor

logger = logging.getLogger(__name__)


async def run_app(shutdown_event: asyncio.Event):
    logger.info("Setting up camera agent...")

    if not environment.camera_stream_url:
        logger.error("CAMERA_STREAM_URL is not set. Exiting.")
        raise RuntimeError("CAMERA_STREAM_URL environment variable is required")

    # initialize
    stream_processor = StreamProcessor(stream_url=environment.camera_stream_url)
    motion_detector = MotionDetectorService(
        detector_frame_size=environment.detector_frame_size,
        enable_object_detection=environment.enable_object_detection,
        model_file=environment.object_detector_model_file,
        label_file=environment.object_detector_label_file,
    )
    post_processor = PostProcessor(
        fps=environment.postprocessor_fps,
        frame_size=environment.postprocessor_frame_size,
        detector_frame_size=environment.detector_frame_size,
        storage_dir=environment.postprocessor_recorder_storage_dir,
    )

    # hook up
    stream_processor.set_frame_callback(motion_detector.process)
    motion_detector.set_motion_callback(post_processor.process)

    try:
        await stream_processor.start()
        await shutdown_event.wait()
    except Exception as e:
        logger.error(f"Unhandled exception: {e}")
    finally:
        logger.info("Shutting down...")
        await stream_processor.stop()
        logger.info("Camera agent shutdown complete.")
