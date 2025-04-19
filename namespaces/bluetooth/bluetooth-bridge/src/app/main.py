#!/usr/bin/python3
 
import logging 
import airthings.tasks
from apscheduler.schedulers.blocking import BlockingScheduler  
from apscheduler.triggers.interval import IntervalTrigger  
import bluetooth.tasks
from common import task_queue  
import bluetooth
import airthings 

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s') 

logging.info("Starting Bluetooth scan scheduler...") 
scheduler = BlockingScheduler() 

def queue_task(task):
    try:
        task_queue.add_task(task)
    except Exception as e:
        logging.error(f"Failed to add task to queue: {e}")

try:
    task_queue.start_queue_worker()
    
    # Generic bluetooth tasks
    scheduler.add_job(
        lambda: queue_task(bluetooth.tasks.scan_task), 
        trigger=IntervalTrigger(minutes=1), 
        name=bluetooth.tasks.scan_task.__name__
    )

    # Airthings tasks
    scheduler.add_job(
        lambda: queue_task(airthings.tasks.wave_plus_sensor_data_basement_task), 
        trigger=IntervalTrigger(minutes=15), 
        name=airthings.tasks.wave_plus_sensor_data_basement_task.__name__
    )
    scheduler.add_job(
        lambda: queue_task(airthings.tasks.wave_plus_sensor_data_livingroom_task), 
        trigger=IntervalTrigger(minutes=15), 
        name=airthings.tasks.wave_plus_sensor_data_livingroom_task.__name__
    )
    scheduler.add_job(
        lambda: queue_task(airthings.tasks.wave_plus_sensor_data_bedroom_task), 
        trigger=IntervalTrigger(minutes=15), 
        name=airthings.tasks.wave_plus_sensor_data_bedroom_task.__name__
    )
    
    # Start the scheduler
    scheduler.start() 
except (KeyboardInterrupt, SystemExit):
    task_queue.stop_queue_worker()
    scheduler.shutdown()
    logging.info("Scheduler stopped.")