import dataclasses
import json
import uuid
from bluetooth.service import scan, connect, send_command
from common import kafka
import logging
from typing import TypedDict, NotRequired


class ScanAndPublishKwargs(TypedDict):
    timeout: NotRequired[int]
    kafka_topic: str


async def scan_and_publish(timeout: int, kafka_topic: str):
    try:
        logging.info("Starting Bluetooth scan...") 
        response = await scan(timeout)
        logging.info(f"Scan completed with {len(response)} devices found.")
        payload = json.dumps(response)
        kafka.produce(kafka_topic, payload.encode("utf-8"))
    except Exception as e:
        logging.error(f"Unexpected error while scanning ble: {e}")


class ConnectAndPublishKwargs(TypedDict):
    address: str
    kafka_topic: str


async def connect_and_publish(address: str, kafka_topic: str):
    try:
        logging.info(f"Connecting to Bluetooth device {address}...")
        response = await connect(address)
        payload = json.dumps(dataclasses.asdict(response))
        kafka.produce(kafka_topic, payload.encode("utf-8"))
    except Exception as e:
        logging.error(f"Unexpected error while connecting to {address}: {e}")


class SendCommandAndPublishKwargs(TypedDict):
    address: str
    characteristic: str
    command: str
    format_type: str
    kafka_topic: str


async def send_command_and_publish(
    address: str, characteristic: str, command: str, format_type: str, kafka_topic: str
):
    try:
        response = await send_command(
            address=address,
            characteristic=uuid.UUID(characteristic),
            command=bytearray(command, "utf-8"),
            format_type=format_type,
        )
        if not response:
            logging.warning(
                f"No response received from {address} for command {command}."
            )
        else:
            kafka.produce(kafka_topic, response)
    except Exception as e:
        logging.error(f"Unexpected error while sending command to {address}: {e}")
