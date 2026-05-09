#!/usr/bin/env python3
"""Matrix Backup Notification Bot - receives webhook notifications and posts to Matrix."""

import asyncio
import os

from aiohttp import web
from nio import AsyncClient, LoginResponse
import logging

# Configuration
MATRIX_SERVER = os.environ["MATRIX_SERVER"]
MATRIX_USER = os.environ["MATRIX_USER"]
MATRIX_PASSWORD = os.environ.get("MATRIX_PASSWORD", "")
MATRIX_TOKEN = os.environ.get("MATRIX_TOKEN", "")
MATRIX_ROOM = os.environ["MATRIX_ROOM"]
WEBHOOK_PORT = int(os.getenv("WEBHOOK_PORT", "9090"))
 
# Ensure the homeserver URL includes a scheme so aiohttp gets a valid URL
if not MATRIX_SERVER.startswith("http://") and not MATRIX_SERVER.startswith("https://"):
    MATRIX_SERVER = "https://" + MATRIX_SERVER


# Logging setup
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(
    level=LOG_LEVEL,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger("backup-bot")
logging.getLogger("aiohttp").setLevel(logging.WARNING)
logging.getLogger("nio").setLevel(logging.INFO) 
logger.info("Starting Matrix Backup Bot for server %s, user %s, room %s", MATRIX_SERVER, MATRIX_USER, MATRIX_ROOM)

class BackupBot:
    """Simple webhook-to-Matrix notification bot."""

    def __init__(self):
        self.client = AsyncClient(MATRIX_SERVER, MATRIX_USER)
        self.room_id = MATRIX_ROOM

    async def login(self):
        if MATRIX_TOKEN:
            self.client.access_token = MATRIX_TOKEN
            self.client.user_id = MATRIX_USER
        else:
            try:
                response = await self.client.login(MATRIX_PASSWORD)
            except Exception:
                logger.exception("Matrix login request failed")
                raise
            if not isinstance(response, LoginResponse):
                logger.error("Login failed: %s", response)
                raise Exception(f"Login failed: {response}")
            logger.info("Logged in as %s", self.client.user_id)

    async def send(self, message: str):
        await self.client.room_send(
            self.room_id,
            "m.room.message",
            {"msgtype": "m.text", "body": message},
        )

    async def run(self):
        await self.login()
        await self.send("🤖 Backup notification bot started")
        logger.info("Bot started and connected to Matrix homeserver %s", MATRIX_SERVER)
        await self.run_webhook()

    async def run_webhook(self):
        """HTTP webhook to receive backup notifications."""

        async def handle_webhook(request):
            data = await request.json()
            status = data.get("status", "unknown")
            message = data.get("message", "")

            # Map status to icon
            icon_map = {
                "ok": "✅",
                "error": "❌",
                "warn": "⚠️",
                "info": "ℹ️",
            }
            icon = icon_map.get(status.lower(), "📝")

            # Format message for Matrix
            if message:
                msg = f"{icon} {message}"
            else:
                msg = f"{icon} Backup notification (status: {status})"

            try:
                await self.send(msg)
                return web.json_response({"status": "ok"})
            except Exception:
                logger.exception("Failed to send message to Matrix")
                return web.json_response({"error": "internal error"}, status=500)

        async def health_check(request):
            return web.json_response({"status": "healthy"})

        app = web.Application()
        app.router.add_post("/webhook", handle_webhook)
        app.router.add_get("/health", health_check)

        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, "0.0.0.0", WEBHOOK_PORT)
        await site.start()
        logger.info("Webhook listening on port %s", WEBHOOK_PORT)

        # Keep running
        while True:
            await asyncio.sleep(3600)

    async def close(self):
        """Close underlying nio client session."""
        try:
            await self.client.close()
        except Exception:
            pass


async def main():
    bot = BackupBot()
    try:
        await bot.run()
    finally:
        await bot.close()


if __name__ == "__main__":
    asyncio.run(main())