#!/usr/bin/python3
 
import logging 
import airthings.tasks
from apscheduler.schedulers.blocking import BlockingScheduler
import bluetooth.tasks
from common import task_queue  
import bluetooth
import airthings 

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s') 

logging.info("Starting Bluetooth scan scheduler...") 
scheduler = BlockingScheduler() 

try:
    task_queue.start_queue_worker() 
    bluetooth.tasks.schedule_scan(scheduler) 
    airthings.tasks.schedule_basement(scheduler)
    airthings.tasks.schedule_living_room(scheduler)
    airthings.tasks.schedule_bedroom(scheduler)
    scheduler.start() 
except (KeyboardInterrupt, SystemExit):
    task_queue.stop_queue_worker()
    scheduler.shutdown()
    logging.info("Scheduler stopped.")