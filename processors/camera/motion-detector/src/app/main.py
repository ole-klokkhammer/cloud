#!/usr/bin/python3

import os
import logging
import env as environment
from detector.motion_detector import MotionDetector
from kafka import KafkaProducer

 
logging.basicConfig(
    level=logging._nameToLevel[environment.log_level.upper()] , 
    format="%(asctime)s %(levelname)s %(message)s"
)

if __name__ == "__main__":   
    logging.info("Starting motion detector...")
    logging.info(f"Using stream URL: {environment.entrance_roof_stream_url}") 
    
    producer = KafkaProducer(
        bootstrap_servers=environment.kafka_bootstrap_servers,
        value_serializer=lambda v: v,  # Send bytes
        max_request_size=4 * 1024 * 1024,
        enable_auto_commit=True,
    )

    motion_detector = MotionDetector(
        stream_url=environment.entrance_roof_stream_url,
        kafka_producer=producer,
        kafka_topic=environment.kafka_topic,
    )

    motion_detector.run()
