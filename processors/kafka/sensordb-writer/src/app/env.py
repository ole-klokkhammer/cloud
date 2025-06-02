#!/usr/bin/python3
import os


log_level = os.environ.get("LOG_LEVEL", "INFO").upper()

kafka_broker = os.environ.get("KAFKA_BROKER")
kafka_topic = os.environ.get("KAFKA_TOPIC")
db_host = os.environ.get("DB_HOST")
db_port = os.environ.get("DB_PORT", "5432")
db_user = os.environ.get("DB_USER")
db_password = os.environ.get("DB_PASSWORD")
db_name = os.environ.get("DB_NAME")

mqtt_broker = os.getenv("MQTT_BROKER", "192.168.10.207")   
mqtt_port = int(os.getenv("MQTT_PORT", 1883))  # Default to 1883 if not set
mqtt_client_id = os.getenv("MQTT_CLIENT_ID", "bluetooth_bridge")  # Default to "bluetooth_bridge" if not set
