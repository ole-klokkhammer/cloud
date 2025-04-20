import json
import logging 
import airthings.device 
from common.utils import publish_payload
from apscheduler.triggers.cron import CronTrigger
import airthings

async def update_sensor_data(mac, topic):
    try:
        response = await airthings.device.read_wave_plus_read_sensor_data(mac)
        logging.debug(f"Result: {response}")
        publish_payload(topic, json.dumps(response.__dict__))  
    except Exception as e:
        logging.error(f"Unexpected error reading sensor data from {mac}: {e}")


async def update_wave_plus_battery(mac, topic):
    try:
        response = await airthings.device.read_wave_plus_battery(mac)
        logging.debug(f"Result: {response}")
        publish_payload(topic, json.dumps(response.__dict__))
    except Exception as e:
        logging.error(f"Unexpected error reading battery from {mac}: {e}")
