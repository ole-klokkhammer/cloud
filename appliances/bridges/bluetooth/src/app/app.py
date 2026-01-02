import asyncio
import json
from aiomqtt import Client
from bleak import BleakScanner, BleakClient

MQTT_BROKER = "hivemq.home.lan" # Your MQTT Broker IP
TOPIC_PREFIX = "bluetooth/"
TOPIC_SCAN_REQ = TOPIC_PREFIX + "scan/req"
TOPIC_SCAN_RES = TOPIC_PREFIX + "scan/res"
TOPIC_CONN_REQ = TOPIC_PREFIX + "connect/req"
TOPIC_CONN_RES = TOPIC_PREFIX + "connect/res"

ble_lock = asyncio.Lock()

async def handle_scan(client):
    print("Scanning...")
    devices = await BleakScanner.discover()
    results = [{"name": d.name, "address": d.address} for d in devices]
    await client.publish(TOPIC_SCAN_RES, json.dumps(results))

async def handle_connect(client, payload):
    address = payload.get("address")
    async with ble_lock:
        try:
            async with BleakClient(address, timeout=10.0) as ble_device:
                status = {"address": address, "connected": ble_device.is_connected}
                await client.publish(TOPIC_CONN_RES, json.dumps(status))
        except Exception as e:
            await client.publish(TOPIC_CONN_RES, json.dumps({"error": str(e)}))

async def main():
    async with Client(MQTT_BROKER) as client:
        await client.subscribe(TOPIC_SCAN_REQ)
        await client.subscribe(TOPIC_CONN_REQ)
        
        print("Bluetooth MQTT Bridge started...")
        async with client.messages() as messages:
            async for message in messages:
                if message.topic.matches(TOPIC_SCAN_REQ):
                    asyncio.create_task(handle_scan(client))
                elif message.topic.matches(TOPIC_CONN_REQ):
                    payload = json.loads(message.payload.decode())
                    asyncio.create_task(handle_connect(client, payload))

if __name__ == "__main__":
    asyncio.run(main())