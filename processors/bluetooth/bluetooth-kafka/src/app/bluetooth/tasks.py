
import json
import logging
from common.kafka import produce
from common import task_queue
import bluetooth 
import bluetooth.device  
import bluetooth.utils  
from apscheduler.triggers.cron import CronTrigger
import env 


def schedule_scan(scheduler):   
    """Schedule a Bluetooth scan task."""

    scheduler.add_job(
        lambda: task_queue.add_task(lambda: bluetooth.utils.scan_task()) , 
        trigger=CronTrigger.from_crontab(env.bluetooth_scan_cron), 
        name="bluetooth_scan_task"
    )

def schedule_connect(scheduler):
    """Schedule a connection to a Bluetooth device."""

    tasks = [
        {
            "cron": env.airthings_wave_plus_sensor_data_cron,
            "address": env.airthings_wave_plus_basement,
            "name": "airthings_wave_plus_basement_sensor_data_task"
        },
         {
            "cron": env.airthings_wave_plus_sensor_data_cron,
            "address": env.airthings_wave_plus_living_room,
            "name": "airthings_wave_plus_living_room_sensor_data_task"
        },
         {
            "cron": env.airthings_wave_plus_sensor_data_cron,
            "address": env.airthings_wave_plus_bedroom,
            "name": "airthings_wave_plus_bedroom_sensor_data_task"
        }
    ]
    
    for task in tasks: 
        cron = task["cron"]
        address = task["address"]
        name = task["name"]
        scheduler.add_job(
            lambda: task_queue.add_task(lambda: bluetooth.utils.connect_task(address)) , 
            trigger=CronTrigger.from_crontab(cron),
            name=name
        )
    
def schedule_commands(scheduler):
    """Schedule commands to be sent to Bluetooth devices."""

    wave_plus_command_format_type = "<L2BH2B9H"
    wave_plus_command_battery = "\x6D"
    wave_plus_command_characteristic = "b42e2d06-ade7-11e4-89d3-123b93f75cba"
    tasks = [
        {
            "cron": env.airthings_wave_plus_battery_cron,
            "address": env.airthings_wave_plus_basement,
            "characteristic": wave_plus_command_characteristic,
            "command": wave_plus_command_battery,
            "format_type": wave_plus_command_format_type,
            "name": "airthings_wave_plus_basement_battery_task"
        },
        {
            "cron": env.airthings_wave_plus_battery_cron,
            "address": env.airthings_wave_plus_living_room,
            "characteristic": wave_plus_command_characteristic,
            "command": wave_plus_command_battery,
            "format_type": wave_plus_command_format_type,
            "name": "airthings_wave_plus_living_room_battery_task"
        },
        {
            "cron": env.airthings_wave_plus_battery_cron,
            "address": env.airthings_wave_plus_bedroom,
            "characteristic": wave_plus_command_characteristic,
            "command": wave_plus_command_battery,
            "format_type": wave_plus_command_format_type,
            "name": "airthings_wave_plus_bedroom_battery_task"
        }
    ]

    for task in tasks:
        cron = task["cron"]
        address = task["address"]
        characteristic = task["characteristic"]
        command = task["command"]
        format_type = task["format_type"]
        name = task["name"]
 
        scheduler.add_job(
            lambda: task_queue.add_task(lambda: bluetooth.utils.command_task(
                    address=address,
                    characteristic=characteristic,
                    command=command,
                    format_type=format_type,
                )
            ), 
            trigger=CronTrigger.from_crontab(cron),
            name=name
        )