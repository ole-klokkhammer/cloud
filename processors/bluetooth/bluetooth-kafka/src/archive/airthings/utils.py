import dataclasses
import json
import logging 
import airthings.device 
import bluetooth.device
from common.utils import publish_payload
from common.kafka import produce
from apscheduler.triggers.cron import CronTrigger
import airthings

async def update_sensor_data(mac):
    try: 
        key = "airthings/" + mac + "/data"
        payload = await bluetooth.device.connect(mac)
        produce(key, json.dumps(dataclasses.asdict(payload)))
    except Exception as e:
        logging.error(f"Unexpected error reading sensor data from {mac}: {e}")


async def update_wave_plus_battery(mac):
    try:
        topic = "bluetooth/airthings/" + mac + "/battery"
        response = await airthings.device.read_wave_plus_battery(mac)
        logging.debug(f"Result: {response}")
        produce(topic, json.dumps(response.__dict__))
    except Exception as e:
        logging.error(f"Unexpected error reading battery from {mac}: {e}")
