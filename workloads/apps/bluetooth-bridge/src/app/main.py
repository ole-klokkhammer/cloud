import asyncio
import json
from aiomqtt import Client
from bluetooth import service as bt_service
import env
import logging

MQTT_BROKER = "hivemq.home.lan"  # Your MQTT Broker IP
TOPIC_PREFIX = "bluetooth"
TOPIC_SCAN = f"{TOPIC_PREFIX}/scan"
TOPIC_SCAN_RESULT = f"{TOPIC_PREFIX}/scan/result"
TOPIC_SCAN_ERROR = f"{TOPIC_PREFIX}/scan/error"
TOPIC_CONNECT = f"{TOPIC_PREFIX}/+/connect"  # bluetooth/{address}/connect
TOPIC_COMMAND = f"{TOPIC_PREFIX}/+/command/+"  # bluetooth/{address}/command/{characteristic}


logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)


async def handle_scan(client):
    logger.info("Scanning...")
    try:
        devices = await bt_service.scan(env.scan_timeout)
        await client.publish(TOPIC_SCAN_RESULT, json.dumps(devices))
    except Exception as e:
        logger.error(f"Scan failed: {e}")
        await client.publish(TOPIC_SCAN_ERROR, json.dumps({"error": str(e)}))


async def handle_connect(client, address):
    logger.info(f"Connecting to {address}...")
    result_topic = f"{TOPIC_PREFIX}/{address}/connect/result"
    error_topic = f"{TOPIC_PREFIX}/{address}/connect/error"
    try:
        status = await bt_service.connect(address, env.connect_timeout)
        await client.publish(result_topic, json.dumps(status, default=vars))
    except Exception as e:
        logger.error(f"Connect to {address} failed: {e}")
        await client.publish(error_topic, json.dumps({"error": str(e)}))


async def handle_command(client, address, characteristic, payload):
    """
    Expected payload:
    {
        "command": "01020304",  # hex string
        "format_type": "<BBBB"  # struct format for expected response (optional)
    }
    """
    command_hex = payload.get("command")
    format_type = payload.get("format_type", "<B")  # default: single byte
    result_topic = f"{TOPIC_PREFIX}/{address}/command/{characteristic}/result"
    error_topic = f"{TOPIC_PREFIX}/{address}/command/{characteristic}/error"
    
    try:
        import uuid
        char_uuid = uuid.UUID(characteristic)
        command_bytes = bytearray.fromhex(command_hex)
        
        result = await bt_service.send_command(
            address, char_uuid, command_bytes, format_type
        )
        
        response = {
            "address": address,
            "characteristic": characteristic,
            "response": result.hex() if result else None,
        }
        await client.publish(result_topic, json.dumps(response))
    except Exception as e:
        logger.error(f"Command to {address}/{characteristic} failed: {e}")
        await client.publish(error_topic, json.dumps({"error": str(e)}))


async def main():
    async with Client(MQTT_BROKER) as client:
        await client.subscribe(TOPIC_SCAN)
        await client.subscribe(TOPIC_CONNECT)
        await client.subscribe(TOPIC_COMMAND)

        logger.info("Bluetooth MQTT Bridge started...")
        async for message in client.messages:
            logger.info(f"Received message on topic: {message.topic}")
            topic_parts = str(message.topic).split("/")
            
            if message.topic.matches(TOPIC_SCAN):
                asyncio.create_task(handle_scan(client))
                
            elif message.topic.matches(TOPIC_CONNECT):
                # Topic: bluetooth/{address}/connect
                address = topic_parts[1]
                asyncio.create_task(handle_connect(client, address))
                
            elif message.topic.matches(TOPIC_COMMAND):
                # Topic: bluetooth/{address}/command/{characteristic}
                address = topic_parts[1]
                characteristic = topic_parts[3]
                payload = json.loads(message.payload.decode()) if message.payload else {}
                asyncio.create_task(handle_command(client, address, characteristic, payload))


if __name__ == "__main__":
    asyncio.run(main())
