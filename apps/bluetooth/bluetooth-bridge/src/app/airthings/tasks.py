 
import airthings.utils
from common import task_queue
from apscheduler.triggers.cron import CronTrigger
import env
import airthings


def schedule(scheduler, mac, sensor_name):
    async def sensor_task():
        await airthings.utils.update_sensor_data(mac, sensor_name)

    async def battery_task():
        await airthings.utils.update_wave_plus_battery(mac, sensor_name)

    scheduler.add_job(
        lambda: task_queue.add_task(sensor_task), 
        trigger=CronTrigger.from_crontab(env.airthings_wave_plus_sensor_data_cron), 
        name=f"airthings_wave_plus_sensor_data_{sensor_name}_task"
    )

    scheduler.add_job(
        lambda: task_queue.add_task(battery_task), 
        trigger=CronTrigger.from_crontab(env.airthings_wave_plus_battery_cron), 
        name=f"airthings_wave_plus_battery_{sensor_name}_task"
    )


def schedule_basement(scheduler):  
    schedule(scheduler, env.airthings_wave_plus_basement,  "basement")

def schedule_living_room(scheduler):
    schedule(scheduler, env.airthings_wave_plus_living_room, "living_room")

def schedule_bedroom(scheduler):    
    schedule(scheduler, env.airthings_wave_plus_bedroom, "bedroom")