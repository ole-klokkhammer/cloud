
import json
import logging
import bluetooth
from paho.mqtt import MQTTException, publish
import bluetooth.device
from env import mqtt_broker, mqtt_port, mqtt_client_id

async def scan_task(): 
    try:
        response = await bluetooth.device.scan(5)
        logging.debug(f"Bluetooth scan result: {response}")
        publish.single(
            "bluetooth/scan", 
            payload=json.dumps(response), 
            hostname=mqtt_broker, 
            port=mqtt_port,
            client_id=mqtt_client_id,
        ) 
    except MQTTException as e:
        logging.error(f"Failed to publish to MQTT: {e}")
    except Exception as e:
        logging.error(f"Unexpected error publishing to MQTT: {e}")
