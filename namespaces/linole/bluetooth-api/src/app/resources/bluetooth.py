#!/usr/bin/python3
import asyncio
import struct
import uuid
from dataclasses import field, dataclass
from typing import Any, Optional, Dict

import resources.utils as utils
from bleak import BleakScanner, AdvertisementData, BLEDevice, BleakClient, BleakError


@dataclass
class Value:
    hex: str
    utf8: str


@dataclass
class Descriptor:
    description: str
    value: Optional[Value] = field(default_factory=dict)
    error: Optional[str] = None


@dataclass
class Characteristic:
    description: str
    properties: list
    value: Optional[Value] = None
    error: Optional[str] = None
    descriptors: Dict[str, Descriptor] = field(default_factory=dict)


@dataclass
class Service:
    description: str
    characteristics: Dict[str, Characteristic] = field(default_factory=dict)


@dataclass
class BLEDeviceResponse:
    services: Dict[str, Service] = field(default_factory=dict)


async def scan(timeout: int):
    devices: dict[str, tuple[BLEDevice, AdvertisementData]] = await BleakScanner.discover(
        return_adv=True,
        timeout=timeout
    )

    return [
        {
            "name": device.name,
            "address": device.address,
            "rssi": ad_data.rssi,
            "manufacturer_data": {
                k: utils.hex_bytes_as_str(v)
                for k, v in ad_data.manufacturer_data.items()
            },
        }
        for device, ad_data in devices.values()
    ]


async def connect(address: str) -> BLEDeviceResponse:
    result = BLEDeviceResponse()
    async with BleakClient(address) as client:
        for service in client.services:
            service_info = Service(description=service.description)
            for characteristic in service.characteristics:
                char_value = Characteristic(
                    description=characteristic.description,
                    properties=characteristic.properties,
                )

                # Read characteristic value
                try:
                    if "read" in characteristic.properties:
                        gatt_value = await client.read_gatt_char(characteristic.uuid)
                        char_value.value = Value(
                            hex=utils.hex_bytes_as_str(gatt_value),
                            utf8=gatt_value.decode("utf-8", errors="ignore")
                        )
                    else:
                        char_value.value = None
                except BleakError as e:
                    char_value.error = str(e)

                # Read descriptors
                for descriptor in characteristic.descriptors:
                    desc_value = Descriptor(description=descriptor.description)
                    try:
                        desc_data = await client.read_gatt_descriptor(descriptor.handle)
                        desc_value.value = Value(
                            hex=utils.hex_bytes_as_str(desc_data),
                            utf8=desc_data.decode("utf-8", errors="ignore")
                        )
                    except BleakError as e:
                        desc_value.error = str(e)
                    char_value.descriptors[descriptor.uuid] = desc_value

                service_info.characteristics[characteristic.uuid] = char_value

            result.services[service.uuid] = service_info

    return result


async def send_command(
        address: str,
        characteristic: uuid.UUID,
        command: bytearray,
        format_type: str
) -> bytearray | None:
    notification = NotificationReceiver(characteristic, format_type)
    async with BleakClient(address) as client:
        await client.start_notify(characteristic, notification)
        await client.write_gatt_char(characteristic, command)
        await notification.wait_for_message(5)
        await client.stop_notify(characteristic)
    return notification.message


class NotificationReceiver:
    message: bytearray | None

    def __init__(self, characteristic: uuid.UUID, format_type: str):
        self.message = None
        self.characteristic = characteristic
        self.format_type = format_type
        self._message_size = struct.calcsize(self.format_type)
        self._loop = asyncio.get_running_loop()
        self._future: asyncio.Future[None] = self._loop.create_future()

    def _full_message_received(self) -> bool:
        return self.message is not None and len(self.message) >= self._message_size

    def __call__(self, _: Any, data: bytearray) -> None:
        if self.message is None:
            self.message = data
        elif not self._full_message_received():
            self.message += data

        if self._full_message_received():
            self._future.set_result(None)

    def _on_timeout(self) -> None:
        if not self._future.done():
            self._future.set_exception(
                asyncio.TimeoutError("Timeout waiting for message")
            )

    async def wait_for_message(self, timeout: float) -> None:
        if not self._full_message_received():
            timer_handle = self._loop.call_later(timeout, self._on_timeout)
            try:
                await self._future
            finally:
                timer_handle.cancel()
