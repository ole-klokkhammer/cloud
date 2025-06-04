#!/usr/bin/python3
 
import logging  
from apscheduler.schedulers.blocking import BlockingScheduler
import bluetooth.schedules
import bluetooth.tasks
from common import task_queue  
import bluetooth 

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s') 

logging.info("Starting Bluetooth scan scheduler...") 
scheduler = BlockingScheduler() 

try:
    task_queue.start_queue_worker() 

    bluetooth.schedules.schedule_scan(scheduler) 
    bluetooth.schedules.schedule_connect(scheduler) 
    bluetooth.schedules.schedule_commands(scheduler) 
    
    scheduler.start() 
except (KeyboardInterrupt, SystemExit):
    task_queue.stop_queue_worker()
    scheduler.shutdown()
    logging.info("Scheduler stopped.")