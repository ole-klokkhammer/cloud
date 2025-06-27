#!/usr/bin/python3

import logging
import signal
import env as environment
from services.motion_detector import (
    MotionDetector,
    CameraConfig,
    ObjectDetectorConfig,
    KafkaConfig,
    RestreamerConfig,
    MotionDetectorConfig,
)

logging.basicConfig(
    level=logging._nameToLevel[environment.log_level.upper()],
    format="%(asctime)s %(levelname)s %(message)s",
)

if __name__ == "__main__":
    assert environment.entrance_roof_stream_url, "ENTRANCE_ROOF_STREAM_URL must be set"
    assert environment.kafka_bootstrap_servers, "KAFKA_BOOTSTRAP_SERVERS must be set"
    assert environment.kafka_topic, "KAFKA_TOPIC must be set"

    motion_detector = MotionDetector(
        motion_detector_config=MotionDetectorConfig(
            frame_width=environment.motion_detector_frame_width,
            frame_height=environment.motion_detector_frame_height,
        ),
        camera_config=CameraConfig(
            stream_url=environment.entrance_roof_stream_url,
            camera_id=environment.entrance_roof_stream_url,
        ),
        object_detector_config=(
            ObjectDetectorConfig(
                model_file=environment.object_detector_model_file,
                label_file=environment.object_detector_label_file,
            )
            if environment.enable_object_detection
            else None
        ),
        restreamer_config=(
            RestreamerConfig(
                stream_name=environment.restreamer_stream_name,
                frame_size=(
                    environment.motion_detector_frame_width,
                    environment.motion_detector_frame_height,
                ),
                fps=environment.restreamer_fps,
            )
            if environment.enable_restreamer
            else None
        ),
        kafka_config=(
            KafkaConfig(
                bootstrap_servers=environment.kafka_bootstrap_servers,
                topic=environment.kafka_topic,
            )
            if environment.enable_kafka
            else None
        ),
    )

    def shutdown(signum, frame):
        logging.info(f"Received signal {signum}, shutting down...")
        motion_detector.stop()
        exit(0)

    # Register signal handlers
    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)

    motion_detector.start()
