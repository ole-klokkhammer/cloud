#!/usr/bin/python3

import asyncio
import logging
import signal
from app.app import run_app
import env as environment

logging.basicConfig(
    level=logging._nameToLevel[environment.log_level.upper()],
    format="%(asctime)s %(levelname)s %(message)s",
)
logger = logging.getLogger(__name__)


async def main():
    shutdown_event = asyncio.Event()

    loop = asyncio.get_running_loop()
    loop.add_signal_handler(signal.SIGINT, lambda: shutdown_event.set())
    loop.add_signal_handler(signal.SIGTERM, lambda: shutdown_event.set())

    app_task = asyncio.create_task(run_app(shutdown_event), name="app")
    app_task.add_done_callback(lambda _: shutdown_event.set()) # ensure shutdown app is done/raised exception

    try:
        await shutdown_event.wait()
        try:
            logger.info("Shutdown requested, waiting for app to finish...")
            await asyncio.wait_for(app_task, timeout=10.0)
        except asyncio.TimeoutError:
            logger.warning("App did not finish in time, cancelling task...")
            app_task.cancel()
            try:
                await app_task
            except asyncio.CancelledError:
                logger.info("App task cancelled")
    except asyncio.CancelledError:
        logger.info("Main cancelled")
        raise
    finally:
        logger.info("Main exiting")


if __name__ == "__main__":
    asyncio.run(main())
