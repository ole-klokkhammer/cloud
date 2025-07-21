#!/usr/bin/python3

import logging
import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import bluetooth.schedules
import bluetooth

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")


async def main():
    logging.info("Starting Bluetooth scan scheduler...")
    scheduler = AsyncIOScheduler()
    bluetooth.schedules.schedule_scan(scheduler)
    bluetooth.schedules.schedule_connect(scheduler)
    bluetooth.schedules.schedule_commands(scheduler)
    scheduler.start()

    try:
        while True:
            await asyncio.sleep(1)
    except (KeyboardInterrupt, SystemExit):
        logging.info("Scheduler stopped.")
    finally:
        logging.info("Exiting Bluetooth scan scheduler.")
        scheduler.shutdown()
        logging.info("Event loop closed.")


if __name__ == "__main__":
    asyncio.run(main())
