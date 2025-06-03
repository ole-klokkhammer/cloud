 
import airthings.utils
from common import task_queue
from apscheduler.triggers.cron import CronTrigger
import env
import airthings


def schedule(scheduler, mac): 
    scheduler.add_job(
        lambda: task_queue.add_task(lambda: airthings.utils.update_sensor_data(mac)), 
        trigger=CronTrigger.from_crontab(env.airthings_wave_plus_sensor_data_cron), 
        name=f"airthings_wave_plus_{mac}_sensor_data_task"
    )

    scheduler.add_job(
        lambda: task_queue.add_task(lambda: airthings.utils.update_wave_plus_battery(mac) ), 
        trigger=CronTrigger.from_crontab(env.airthings_wave_plus_battery_cron), 
        name=f"airthings_wave_plus_{mac}_battery_task"
    )


def schedule_basement(scheduler):  
    schedule(scheduler, env.airthings_wave_plus_basement)

def schedule_living_room(scheduler):
    schedule(scheduler, env.airthings_wave_plus_living_room)

def schedule_bedroom(scheduler):    
    schedule(scheduler, env.airthings_wave_plus_bedroom)