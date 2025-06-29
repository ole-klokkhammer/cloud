#!/usr/bin/python3

import logging
import signal
import env as environment
from services.motion_detector import MotionDetectorService
from services.object_detector import CoralTPUObjectDetectorService
from kafka import KafkaProducer

logging.basicConfig(
    level=logging._nameToLevel[environment.log_level.upper()],
    format="%(asctime)s %(levelname)s %(message)s",
)

if __name__ == "__main__":
    if environment.entrance_roof_stream_url is None:
        logging.error("ENTRANCE_ROOF_STREAM_URL is not set. Exiting.")
        exit(1)
    if environment.kafka_bootstrap_servers is None:
        logging.error("KAFKA_BOOTSTRAP_SERVERS is not set. Exiting.")
        exit(1)

    if environment.LOCAL_DEBUG is False:
        kafka_producer = KafkaProducer(
            bootstrap_servers=environment.kafka_bootstrap_servers,
            value_serializer=lambda v: v,  # Send bytes
        )
    else:
        # disable locally for debugging
        kafka_producer = None
        logging.warning("Kafka disabled, skipping Kafka producer initialization.")

    if environment.enable_object_detection:
        logging.info("Object detection is enabled.")
        object_detector = CoralTPUObjectDetectorService(
            model_file=environment.object_detector_model_file,
            label_file=environment.object_detector_label_file,
        )
    else:
        logging.info("Object detection is disabled.")
        object_detector = None

    entrance_cam_detector = MotionDetectorService(
        stream_url=environment.entrance_roof_stream_url, 
        detector_frame_size=environment.entrance_roof_detector_frame_size,
        output_frame_size=environment.entrance_roof_output_frame_size,
        kafka_topic=environment.kafka_topic,
        kafka_producer=kafka_producer,
        object_detector=object_detector,
    )

    def shutdown(signum, frame):
        logging.info(f"Received signal {signum}, shutting down...")
        entrance_cam_detector.stop()
        exit(0)

    # Register signal handlers
    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)

    entrance_cam_detector.start()
