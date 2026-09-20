"""NATS publisher thread for the detector service.

Background, auto-reconnecting, and *drops nothing while running*:
`publish()` is thread-safe (call_soon_threadsafe onto the loop's queue),
so the capture thread can publish without ever blocking on NATS - stills
keep flowing even when NATS is down. The consumer loop reconnects on
failure and retries after 5s. The thread is a pure daemon: at process
exit it dies with the loop and the kernel closes the socket; items
left in the queue at that moment (a few ms at most) are dropped - the
still on disk is the source of truth.

NOTE: this file is `nats_pub.py` on purpose - a top-level module named
`nats.py` would shadow the nats-py library that `import nats` means.

The module uses the same `"detector"` logger (configured by main.py's
setup_logging at process start), so its lines land in the same journald
stream with the same prefix.
"""

import asyncio
import json
import logging
import threading

import nats

logger = logging.getLogger("detector")


class NatsPub(threading.Thread):
    """background publisher: auto-reconnect; drops nothing while running.

    Pure daemon - no stop()/join(): it dies at process exit, the kernel
    closes the socket, and the NATS server just sees a TCP close.
    """

    def __init__(self, url, subject):
        super().__init__(daemon=True, name="nats")
        self.url, self.subject = url, subject
        self._q = asyncio.Queue()
        self._loop = None

    def publish(self, payload):
        """thread-safe: safe to call from the capture thread (or any thread)."""
        raw = json.dumps(payload, separators=(",", ":")).encode()
        loop = self._loop
        if loop is None or loop.is_closed():
            return  # not running yet - nothing connected anyway
        loop.call_soon_threadsafe(self._q.put_nowait, raw)

    def run(self):
        asyncio.run(self._run())

    async def _run(self):
        self._loop = asyncio.get_running_loop()
        while True:
            try:
                nc = await nats.connect([self.url], name="detector")
                logger.info(f"nats connected: {self.url}")
                while True:
                    item = await self._q.get()
                    await nc.publish(self.subject, item)
            except Exception as e:
                logger.info(
                    f"nats disconnected ({e}); retry in 5s - stills keep flowing"
                )
                await asyncio.sleep(5)
