#!/usr/bin/python3
import os
   
log_level = os.getenv("LOG_LEVEL")     

kafka_broker = os.getenv("KAFKA_BROKER")     
kafka_topic = os.getenv("KAFKA_TOPIC")      

mqtt_broker = os.getenv("MQTT_BROKER", "192.168.10.207")   
mqtt_port = int(os.getenv("MQTT_PORT", 1883))  # Default to 1883 if not set
mqtt_topic = os.getenv("MQTT_TOPIC", "logs/kubernetes/errors/")  
mqtt_client_id = os.getenv("MQTT_CLIENT_ID", "bluetooth_bridge")  # Default to "bluetooth_bridge" if not set
