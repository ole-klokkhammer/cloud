import logging
from common.kafka import produce
import bluetooth
import bluetooth.tasks
from apscheduler.triggers.cron import CronTrigger
import env
import yaml

with open(env.schedules_file) as f:
    config = yaml.safe_load(f)


ble_manufacturer_airthings = "820"


def schedule_scan(scheduler):
    """Schedule a Bluetooth scan task."""

    scan_cfg = config["scan"]
    cron = scan_cfg["cron"]
    kafka_topic = "scan"

    kwargs: bluetooth.tasks.ScanAndPublishKwargs = {
        "timeout": scan_cfg.get("timeout", 10),  # Default to 10 seconds if not provided
        "kafka_topic": kafka_topic,
    }
    scheduler.add_job(
        bluetooth.tasks.scan_and_publish,
        kwargs=kwargs,
        trigger=CronTrigger.from_crontab(cron),
        name="bluetooth_scan_task",
    )


def schedule_connect(scheduler):
    """Schedule a connection to a Bluetooth device."""

    for task in config["connect"]:
        
        cron = task["cron"]
        address = task["address"]
        manufacturer = task["manufacturer"]
        name = f"{address.replace(':', '').lower()}_connect_task"

        # Pass the parameters to the lambda function to avoid late binding issues
        logging.debug(f"Scheduling connect task for {address} with cron {cron}")
        
        kwargs: bluetooth.tasks.ConnectAndPublishKwargs = {
            "address": address,
            "kafka_topic": f"connect/{manufacturer}/{address}",
        }
        scheduler.add_job(
            bluetooth.tasks.connect_and_publish,
            kwargs=kwargs,
            trigger=CronTrigger.from_crontab(cron),
            name=name,
        )


def schedule_commands(scheduler):
    """Schedule commands to be sent to Bluetooth devices."""

    for task in config["command"]:
        cron = task["cron"]
        address = task["address"]
        manufacturer = task["manufacturer"]
        characteristic = task["characteristic"]
        command = task["command"]
        format_type = task["format_type"]
        name = f"{address.replace(':', '').lower()}_command_task"

        # Pass the parameters to the lambda function to avoid late binding issues
        logging.debug(f"Scheduling command task for {address} with cron {cron}")
        kwargs: bluetooth.tasks.SendCommandAndPublishKwargs = {
            "address": address,
            "characteristic": characteristic,
            "command": command,
            "format_type": format_type,
            "kafka_topic": f"command/{manufacturer}/{address}/{characteristic}",
        }
        scheduler.add_job(
            bluetooth.tasks.send_command_and_publish,
            kwargs=kwargs,
            trigger=CronTrigger.from_crontab(cron),
            name=name,
        )
