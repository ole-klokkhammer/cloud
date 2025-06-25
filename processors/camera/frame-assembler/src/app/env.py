#!/usr/bin/python3
import os

log_level = os.environ.get("LOG_LEVEL", "INFO")
LOCAL_DEBUG = os.getenv("LOCAL_DEBUG", "False").lower() in ("true", "1", "yes")

kafka_bootstrap_servers = os.getenv("KAFKA_BOOTSTRAP_SERVERS") 
kafka_topic = os.getenv("KAFKA_TOPIC", "camera_frames")
kafka_group_id = os.getenv("KAFKA_GROUP_ID", "frame_assembler_group")
