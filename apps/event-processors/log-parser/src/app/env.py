#!/usr/bin/python3
import os

mqtt_broker = os.getenv("MQTT_BROKER", "192.168.10.207")   
mqtt_port = int(os.getenv("MQTT_PORT", 1883))  # Default to 1883 if not set
mqtt_client_id = os.getenv("MQTT_CLIENT_ID", "bluetooth_bridge")  # Default to "bluetooth_bridge" if not set
