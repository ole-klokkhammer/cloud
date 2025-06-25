#!/usr/bin/python3
import os

log_level = os.getenv("LOG_LEVEL") 
kafka_bootstrap_servers = os.getenv("KAFKA_BOOTSTRAP_SERVERS") 
entrance_roof_stream_url = os.getenv("ENTRANCE_ROOF_STREAM_URL")
kafka_topic = os.getenv("KAFKA_TOPIC", "camera_frames")