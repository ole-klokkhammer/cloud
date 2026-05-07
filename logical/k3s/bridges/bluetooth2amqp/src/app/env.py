#!/usr/bin/python3
import os

log_level = os.getenv("LOG_LEVEL")
kafka_broker = os.getenv("KAFKA_BROKER")
rabbitmq_host = os.getenv("RABBITMQ_HOST")
schedules_file = os.getenv("SCHEDULES_FILE", "/app/schedules.yaml")
connect_timeout = float(os.getenv("CONNECT_TIMEOUT", 60))
command_timeout = float(os.getenv("COMMAND_TIMEOUT", 60))