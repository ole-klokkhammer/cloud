
import dataclasses
import json
import uuid
import bluetooth.device
from  common import kafka
import logging

async def scan_and_publish(timeout: int = 5): 
    try:
        response = await bluetooth.device.scan(timeout)
        logging.info(f"Scan completed with {len(response)} devices found.")
        payload = json.dumps(response)
        kafka.produce("scan", payload.encode('utf-8'))  
    except Exception as e:
        logging.error(f"Unexpected error while scanning ble: {e}")

async def connect_and_publish(manufacturer: str, address: str):
    try:
        response = await bluetooth.device.connect(address)
        payload = json.dumps(dataclasses.asdict(response))
        kafka.produce("connect/" + manufacturer  + "/" + address, payload.encode('utf-8'))
    except Exception as e:
        logging.error(f"Unexpected error while connecting to {address}: {e}")

async def send_command_and_publish(manufacturer: str, address: str, characteristic: str, command: str, format_type: str):
    try:
        response = await bluetooth.device.send_command(
            address=address,
            characteristic=uuid.UUID(characteristic),
            command=bytearray(command, 'utf-8'),
            format_type=format_type,
        ) 
        if not response:
            logging.warning(f"No response received from {address} for command {command}.")
        else: 
            kafka.produce("command/" + manufacturer + "/" + address + "/" + str(characteristic), response)
    except Exception as e:
        logging.error(f"Unexpected error while sending command to {address}: {e}")

