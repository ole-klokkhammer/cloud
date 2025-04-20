#!/usr/bin/python3
import binascii 
import logging
from paho.mqtt import MQTTException, publish
import env 

def bytes_as_str(value: bytes) -> str:
    return binascii.b2a_hex(value).decode('utf-8', errors='ignore')


def publish_payload(topic, payload: str):
    try:
        publish.single(
            topic, 
            payload=payload, 
            hostname=env.mqtt_broker, 
            port=env.mqtt_port,
            client_id=env.mqtt_client_id,
            retain=True
        ) 
    except MQTTException as e:
        logging.error(f"Failed to publish to MQTT: {e}")
        raise
    except Exception as e:
        logging.error(f"Unexpected error publishing to MQTT: {e}")
        raise
