#!/usr/bin/python3

import os
import logging
import signal
import env as environment
from detector.motion_detector import MotionDetector
from kafka import KafkaProducer


logging.basicConfig(
    level=logging._nameToLevel[environment.log_level.upper()],
    format="%(asctime)s %(levelname)s %(message)s",
)

if __name__ == "__main__":
    logging.info("Starting motion detector...")
    logging.info(f"Using stream URL: {environment.entrance_roof_stream_url}") 

    # producer = KafkaProducer(
    #     bootstrap_servers=environment.kafka_bootstrap_servers,
    #     value_serializer=lambda v: v,  # Send bytes
    #     max_request_size=4 * 1024 * 1024,
    #     compression_type=None,
    #     linger_ms=0,  # Send immediately 
    #     acks=1,
    # )

    motion_detector = MotionDetector(
        stream_url=environment.entrance_roof_stream_url,
       
        kafka_topic=environment.kafka_topic,
    )


    # Register signal handlers
    signal.signal(signal.SIGINT, motion_detector.shutdown)
    signal.signal(signal.SIGTERM, motion_detector.shutdown)

    motion_detector.run()
