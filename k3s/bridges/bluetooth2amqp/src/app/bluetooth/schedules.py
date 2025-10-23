import logging
import bluetooth
import bluetooth.tasks
from apscheduler.triggers.cron import CronTrigger
import env
import yaml

with open(env.schedules_file) as f:
    config = yaml.safe_load(f)


def schedule_scan(scheduler):
    """Schedule a Bluetooth scan task."""

    scan_cfg = config["scan"]
    timeout = scan_cfg.get("timeout", 10)  # Default to 10 seconds if not provided
    cron = scan_cfg["cron"]
    routing_key = scan_cfg["routing_key"]

    scheduler.add_job(
        bluetooth.tasks.scan_and_publish,
        args=[
            bluetooth.tasks.ScanAndPublishParams(
                timeout=timeout, routing_key=routing_key
            )
        ],
        trigger=CronTrigger.from_crontab(cron),
        name="bluetooth_scan_task",
    )


def schedule_connect(scheduler):
    """Schedule a connection to a Bluetooth device."""

    type = "connect"
    for task in config[type]:

        cron = task["cron"]
        address = task["address"]
        routing_key = task["routing_key"]

        logging.debug(f"Scheduling connect task for {address} with cron {cron}")

        scheduler.add_job(
            bluetooth.tasks.connect_and_publish,
            args=[
                bluetooth.tasks.ConnectAndPublishArgs(
                    address=address, routing_key=routing_key
                )
            ],
            trigger=CronTrigger.from_crontab(cron),
            name=f"{routing_key}.{address.replace(':', '').lower()}_task",
        )


def schedule_commands(scheduler):
    """Schedule commands to be sent to Bluetooth devices."""

    for task in config["command"]:
        cron = task["cron"]
        routing_key = task["routing_key"]
        address = task["address"]
        characteristic = task["characteristic"]
        command = task["command"]
        format_type = task["format_type"]

        logging.debug(f"Scheduling command task for {address} with cron {cron}")
        scheduler.add_job(
            bluetooth.tasks.send_command_and_publish,
            args=[
                bluetooth.tasks.SendCommandAndPublishArgs(
                    address=address,
                    characteristic=characteristic,
                    command=command,
                    format_type=format_type,
                    routing_key=routing_key,
                )
            ],
            trigger=CronTrigger.from_crontab(cron),
            name=f"{routing_key}.{address.replace(':', '').lower()}_task",
        )
