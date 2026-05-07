import dataclasses
import json
import uuid
from bluetooth.service import scan, connect, send_command
from common import rabbitmq
import logging
from typing import TypedDict, NotRequired, Literal


class ScanAndPublishParams(TypedDict):
    timeout: NotRequired[int]
    routing_key: str


async def scan_and_publish(params: ScanAndPublishParams):
    timeout = params.get("timeout", 10)
    routing_key = params["routing_key"]
    response = await scan(timeout)
    if not response:
        logging.warning("No devices found during scan.")
        return

    rabbitmq.bluetooth_publish(
        routing_key=routing_key,
        payload=json.dumps(response).encode("utf-8"),
    )


class ConnectAndPublishArgs(TypedDict):
    address: str
    routing_key: str


async def connect_and_publish(params: ConnectAndPublishArgs):
    address = params["address"]
    routing_key = params["routing_key"]
    response = await connect(address)
    if not response:
        logging.warning(f"No response received from {address}.")
        return

    rabbitmq.bluetooth_publish(
        routing_key=routing_key,
        payload=json.dumps(dataclasses.asdict(response)).encode("utf-8"),
        headers={"address": address},
    )


class SendCommandAndPublishArgs(TypedDict):
    address: str
    characteristic: str
    command: str
    format_type: str
    routing_key: str


async def send_command_and_publish(params: SendCommandAndPublishArgs):
    try:
        address = params["address"]
        characteristic = params["characteristic"]
        command = params["command"]
        format_type = params["format_type"]
        routing_key = params["routing_key"]

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
            rabbitmq.bluetooth_publish(
                routing_key=routing_key,
                payload=response,
                headers={
                    "address": address,
                    "characteristic": characteristic,
                    "command": command,
                    "format_type": format_type,
                },
            )
    except Exception as e:
        logging.error(f"Unexpected error while sending command to {params}: {e}")
