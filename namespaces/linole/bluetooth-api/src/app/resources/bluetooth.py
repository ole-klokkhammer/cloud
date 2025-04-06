#!/usr/bin/python3

import binascii
from collections import OrderedDict

from bleak import BleakScanner, AdvertisementData, BLEDevice, BleakClient, BleakError


def hex_bytes_as_str(value: bytes) -> str:
    # return value.decode('utf-8', errors='ignore')
    return binascii.b2a_hex(value).decode('utf-8', errors='ignore')


async def scan(timeout: int) -> [str]:
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
                k: hex_bytes_as_str(v)
                for k, v in ad_data.manufacturer_data.items()
            },
        }
        for device, ad_data in devices.values()
    ]


async def connect(address: str):
    result = OrderedDict()
    async with BleakClient(address) as client:
        services = await client.get_services()
        for service in services:
            service_info = OrderedDict({
                "description": service.description,
                "characteristics": OrderedDict(),
            })
            for characteristic in service.characteristics:
                char_value = OrderedDict({
                    "description": characteristic.description,
                    "properties": characteristic.properties,
                    "value": None,
                    "descriptors": None
                })

                # Read characteristic value
                try:
                    if "read" in characteristic.properties:
                        gatt_value = await client.read_gatt_char(characteristic.uuid)
                        char_value["value"] = {
                            "hex": hex_bytes_as_str(gatt_value),
                            "utf-8": gatt_value.decode("utf-8", errors="ignore")
                        }
                    else:
                        char_value["value"] = None
                except BleakError as e:
                    char_value["error"] = str(e)

                # Read descriptors
                for descriptor in characteristic.descriptors:
                    char_value["descriptors"] = OrderedDict()
                    try:
                        desc_value = await client.read_gatt_descriptor(descriptor.handle)
                        char_value["descriptors"][descriptor.uuid] = {
                            "description": descriptor.description,
                            "value": {
                                "hex": hex_bytes_as_str(desc_value),
                                "utf-8": desc_value.decode("utf-8", errors="ignore")
                            }
                        }
                    except BleakError as e:
                        char_value["descriptors"][descriptor.uuid] = {
                            "error": str(e)
                        }

                service_info["characteristics"][characteristic.uuid] = char_value

            result[service.uuid] = service_info

    return result
