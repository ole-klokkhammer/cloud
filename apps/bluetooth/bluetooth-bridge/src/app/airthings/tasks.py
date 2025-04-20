 
import airthings.utils
from common import task_queue
from apscheduler.triggers.cron import CronTrigger
import env
import airthings


def schedule(scheduler, mac, sensor_name):
    def sensor_task():
        task_queue.add_task(lambda: airthings.utils.update_sensor_data(mac, "bluetooth/airthings/" + sensor_name)) 

    def battery_task():
        task_queue.add_task(lambda: airthings.utils.update_wave_plus_battery(mac, "bluetooth/airthings/" + sensor_name + "/battery")) 

    scheduler.add_job(
        sensor_task, 
        trigger=CronTrigger.from_crontab(env.airthings_wave_plus_sensor_data_cron), 
        name=f"airthings_wave_plus_{sensor_name}_sensor_data_task"
    )

    scheduler.add_job(
        battery_task, 
        trigger=CronTrigger.from_crontab(env.airthings_wave_plus_battery_cron), 
        name=f"airthings_wave_plus_{sensor_name}_battery_task"
    )


def schedule_basement(scheduler):  
    schedule(scheduler, env.airthings_wave_plus_basement,  "basement")

def schedule_living_room(scheduler):
    schedule(scheduler, env.airthings_wave_plus_living_room, "living_room")

def schedule_bedroom(scheduler):    
    schedule(scheduler, env.airthings_wave_plus_bedroom, "bedroom")