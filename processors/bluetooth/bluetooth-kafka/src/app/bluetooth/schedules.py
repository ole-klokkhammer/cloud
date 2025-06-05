import logging
from common.kafka import produce
from common import task_queue
import bluetooth
import bluetooth.tasks
from apscheduler.triggers.cron import CronTrigger
import env

ble_manufacturer_airthings = "820"

def schedule_scan(scheduler):
    """Schedule a Bluetooth scan task."""

    scheduler.add_job(
        lambda: task_queue.add_task(lambda: bluetooth.tasks.scan_and_publish()),
        trigger=CronTrigger.from_crontab(env.bluetooth_scan_cron),
        name="bluetooth_scan_task",
    )


def schedule_connect(scheduler):
    """Schedule a connection to a Bluetooth device."""
 
    tasks = [
        {
            "cron": env.airthings_wave_plus_sensor_data_cron,
            "address": env.airthings_wave_plus_basement,
            "manufacturer": ble_manufacturer_airthings,
        },
        {
            "cron": env.airthings_wave_plus_sensor_data_cron,
            "address": env.airthings_wave_plus_living_room,
            "manufacturer": ble_manufacturer_airthings,
        },
        {
            "cron": env.airthings_wave_plus_sensor_data_cron,
            "address": env.airthings_wave_plus_bedroom,
            "manufacturer": ble_manufacturer_airthings,
        },
    ]

    for task in tasks:
        cron = task["cron"]
        address = task["address"]
        manufacturer = task["manufacturer"]
        name = f"{manufacturer}_{address.replace(':', '').lower()}_sensor_data_task"

        # Pass the parameters to the lambda function to avoid late binding issues
        logging.debug(
            f"Scheduling connect task for {manufacturer} at {address} with cron {cron}"
        )
        scheduler.add_job(
            lambda address=address, manufacturer=manufacturer: task_queue.add_task(
                lambda: bluetooth.tasks.connect_and_publish(
                    manufacturer=manufacturer, address=address
                )
            ),
            trigger=CronTrigger.from_crontab(cron),
            name=name,
        )


def schedule_commands(scheduler):
    """Schedule commands to be sent to Bluetooth devices."""
 
    wave_plus_command_format_type = "<L2BH2B9H"
    wave_plus_command_battery = "\x6d"
    wave_plus_command_characteristic = "b42e2d06-ade7-11e4-89d3-123b93f75cba"
    tasks = [
        {
            "cron": env.airthings_wave_plus_battery_cron,
            "manufacturer": ble_manufacturer_airthings,
            "address": env.airthings_wave_plus_basement,
            "characteristic": wave_plus_command_characteristic,
            "command": wave_plus_command_battery,
            "format_type": wave_plus_command_format_type,
        },
        {
            "cron": env.airthings_wave_plus_battery_cron,
            "manufacturer": ble_manufacturer_airthings,
            "address": env.airthings_wave_plus_living_room,
            "characteristic": wave_plus_command_characteristic,
            "command": wave_plus_command_battery,
            "format_type": wave_plus_command_format_type,
        },
        {
            "cron": env.airthings_wave_plus_battery_cron,
            "manufacturer": ble_manufacturer_airthings,
            "address": env.airthings_wave_plus_bedroom,
            "characteristic": wave_plus_command_characteristic,
            "command": wave_plus_command_battery,
            "format_type": wave_plus_command_format_type,
        },
    ]

    for task in tasks:
        cron = task["cron"]
        address = task["address"]
        manufacturer = task["manufacturer"]
        characteristic = task["characteristic"]
        command = task["command"]
        format_type = task["format_type"]
        name = f"{manufacturer}_{address.replace(':', '').lower()}_sensor_battery_task"

        # Pass the parameters to the lambda function to avoid late binding issues
        logging.debug(
            f"Scheduling command task for {manufacturer} at {address} with cron {cron}"
        )
        scheduler.add_job(
            lambda manufacturer=manufacturer, address=address, characteristic=characteristic, command=command, format_type=format_type: task_queue.add_task(
                lambda: bluetooth.tasks.send_command_and_publish(
                    manufacturer=manufacturer,
                    address=address,
                    characteristic=characteristic,
                    command=command,
                    format_type=format_type,
                )
            ),
            trigger=CronTrigger.from_crontab(cron),
            name=name,
        )
