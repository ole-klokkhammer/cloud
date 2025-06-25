#!/usr/bin/python3

import os
import logging
import env as environment
from assembler.frame_assembler import FrameAssembler
from kafka import KafkaConsumer


logging.basicConfig(
    level=logging._nameToLevel[environment.log_level.upper()] , 
    format="%(asctime)s %(levelname)s %(message)s"
)

logging.info(f"Log level set to: {logging._nameToLevel[environment.log_level.upper()]}")

if __name__ == "__main__":   
    logging.info("Starting frame assembler...")
    logging.info(f"Using kafka topic: {environment.kafka_topic}") 
    
    consumer = KafkaConsumer(
        environment.kafka_topic,
        bootstrap_servers=environment.kafka_bootstrap_servers,
        value_deserializer=lambda x: x,  # Keep as bytes 
        group_id=environment.kafka_group_id,
        enable_auto_commit=False,  # Disable auto-commit to reduce latency
        fetch_min_bytes=1,
        fetch_max_wait_ms=1,  # Reduce wait time for new messages 
    )

    frame_assembler = FrameAssembler( 
        kafka_consumer=consumer
    )

    frame_assembler.run()
