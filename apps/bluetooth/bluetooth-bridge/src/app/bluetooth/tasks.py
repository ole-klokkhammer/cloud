
import json
import logging
from common.utils import publish_payload
from common import task_queue
import bluetooth
from paho.mqtt import MQTTException, publish
import bluetooth.device  
from apscheduler.triggers.cron import CronTrigger
import env

async def scan_task(): 
    try:
        response = await bluetooth.device.scan(5)
        publish_payload("bluetooth/scan", json.dumps(response))  
    except Exception as e:
        logging.error(f"Unexpected error while scanning ble: {e}")

def schedule_scan(scheduler):  
    def task():
        task_queue.add_task(lambda: scan_task()) 

    scheduler.add_job(
        task, 
        trigger=CronTrigger.from_crontab(env.generic_ble_scan_cron), 
        name="bluetooth_scan_task"
    ) 