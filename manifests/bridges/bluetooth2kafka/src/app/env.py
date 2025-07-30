#!/usr/bin/python3
import os

log_level = os.getenv("LOG_LEVEL")
kafka_broker = os.getenv("KAFKA_BROKER")
schedules_file = os.getenv("SCHEDULES_FILE", "/app/schedules.yaml")