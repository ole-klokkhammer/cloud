#!/usr/bin/env python3
"""Matrix AI Bot - Integrates Matrix with vLLM for conversational AI."""

import asyncio
import os
import logging
from aiohttp import ClientSession, web
from nio import AsyncClient, LoginResponse

# Configuration
MATRIX_SERVER = os.environ["MATRIX_SERVER"]
MATRIX_USER = os.environ["MATRIX_USER"]
MATRIX_PASSWORD = os.environ.get("MATRIX_PASSWORD", "")
MATRIX_TOKEN = os.environ.get("MATRIX_TOKEN", "")
MATRIX_ROOM = os.environ["MATRIX_ROOM"]
VLLM_API_URL = os.environ.get("VLLM_API_URL", "http://core-gpu.home.lan:8000/v1")
VLLM_MODEL = os.environ.get("VLLM_MODEL", "gemma-4-31b-nvfp4")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()

# Ensure the homeserver URL includes a scheme
if not MATRIX_SERVER.startswith("http://") and not MATRIX_SERVER.startswith("https://"):
    MATRIX_SERVER = "https://" + MATRIX_SERVER

# Logging setup
logging.basicConfig(
    level=LOG_LEVEL,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger("matrix-ai-bot")

class AIBot:
    """Matrix bot that interfaces with a vLLM API."""

    def __init__(self):
        self.client = AsyncClient(MATRIX_SERVER, MATRIX_USER)
        self.room_id = MATRIX_ROOM
        self.session = None

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

    async def get_ai_response(self, prompt: str) -> str:
        """Calls the vLLM API to get a completion."""
        url = f"{VLLM_API_URL}/chat/completions"
        payload = {
            "model": VLLM_MODEL,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 512,
            "temperature": 0.7,
        }
        
        try:
            async with self.session.post(url, json=payload) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return data["choices"][0]["message"]["content"]
                else:
                    text = await resp.text()
                    logger.error("vLLM API error %s: %s", resp.status, text)
                    return "❌ AI Error: Failed to get response from vLLM."
        except Exception:
            logger.exception("Exception calling vLLM API")
            return "❌ AI Error: Connection to vLLM failed."

    async def run(self):
        await self.login()
        self.session = ClientSession()
        logger.info("AI Bot started, monitoring room %s", self.room_id)
        
        # Use a sync loop to listen for messages
        # We only care about messages in our configured room
        # and messages that are not from the bot itself.
        
        # For simplicity in this version, we sync until we find a new message
        # In a production bot, we'd handle token management and pagination.
        
        # Initial sync to clear old events
        await self.client.sync(timeout=30000)
        
        while True:
            response = await self.client.sync(timeout=30000)
            
            for event in response["room_id"].get("next_batch", []):
                if event.type == "m.room.message" and event.sender != self.client.user_id:
                    # Check if it's in the right room and if it's a message to us
                    # (e.g. mentions us or we are in a dedicated AI room)
                    if event.room_id == self.room_id:
                        content = event.body
                        
                        # Trigger: Bot is mentioned or it's a direct message in the AI room
                        if f"@{self.client.user_id}" in content or "AI" in self.room_id:
                            logger.info("Processing message from %s: %s", event.sender, content)
                            
                            # Clean the prompt (remove mention)
                            prompt = content.replace(f"@{self.client.user_id}", "").strip()
                            
                            # Get AI response
                            response_text = await self.get_ai_response(prompt)
                            
                            # Send back to Matrix
                            await self.send(response_text)
            
            await asyncio.sleep(1)

    async def close(self):
        if self.session:
            await self.session.close()
        await self.client.close()

async def main():
    bot = AIBot()
    try:
        await bot.run()
    finally:
        await bot.close()

if __name__ == "__main__":
    asyncio.run(main())