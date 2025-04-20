import json
import logging 
import airthings.device 
from common.utils import publish_payload
from apscheduler.triggers.cron import CronTrigger
import airthings

async def update_sensor_data(device_id, name):
    try:
        response = await airthings.device.read_wave_plus_read_sensor_data(device_id)
        logging.debug(f"Result: {response}")
        publish_payload("bluetooth/airthings/" + name, json.dumps(response.__dict__))  
    except Exception as e:
        logging.error(f"Unexpected error reading sensor data: {e}")


async def update_wave_plus_battery(mac, name):
    try:
        response = await airthings.device.read_wave_plus_battery(mac)
        logging.debug(f"Result: {response}")
        publish_payload("bluetooth/airthings/" + name + "/battery", json.dumps(response.__dict__))
    except Exception as e:
        logging.error(f"Unexpected error reading battery: {e}")
