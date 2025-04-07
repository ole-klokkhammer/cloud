#!/usr/bin/python3
import binascii
import logging
import struct
from typing import Optional
from resources import bluetooth

# https://github.com/Airthings/airthings-ble/blob/main/airthings_ble/const.py

wave_plus_command_format_type = "<L2BH2B9H"
wave_plus_connect_format_type = "<4B8H"


async def wave_plus_read_sensor_data(address: str):
    response = await bluetooth.connect(address=address)
    service = response.services["b42e1c08-ade7-11e4-89d3-123b93f75cba"]
    characteristic = service.characteristics["b42e2a68-ade7-11e4-89d3-123b93f75cba"]
    return wave_plus_sensor_data(bytearray.fromhex(characteristic.value.hex))


def wave_plus_manufacturer_data(value: bytearray) -> Optional[int]:
    if not value or value == "None":
        return None
    return value[0] | (value[1] << 8) | (value[2] << 16) | (value[3] << 24)


def wave_plus_sensor_data(raw_data: bytearray) -> dict[str, float | None | str]:
    val = struct.unpack(wave_plus_connect_format_type, raw_data)
    return {
        "humidity": val[1] / 2.0,
        "illuminance": int(val[2] / 255 * 100),
        "radon_1day_avg": val[4],
        "radon_longterm_avg": val[5],
        "temperature": val[6] / 100.0,
        "pressure": val[7] / 50.0,
        "co2": val[8] * 1.0,
        "voc": val[9] * 1.0,
        # "extra1": val[10] * 1.0,
        # "extra2": val[11] * 1.0
    }


async def read_wave_plus_battery(address: str) -> Optional[float]:
    response = await bluetooth.send_command(
        address=address,
        characteristic="b42e2d06-ade7-11e4-89d3-123b93f75cba",
        command=bytearray(b"\x6D"),
        format_type=wave_plus_command_format_type,
    )

    cmd = response[0:1]
    logging.info("Command: %s", binascii.b2a_hex(cmd).decode('utf-8', errors='ignore'))

    data = struct.unpack(wave_plus_command_format_type, response[2:])
    logging.info("Data: %s", data)

    battery_volt = float(data[13] / 1000.0)
    bat_per = battery_percentage(battery_volt)
    return bat_per if bat_per else None


def battery_percentage(voltage: float) -> int:
    return round(_two_batteries(voltage))


def _two_batteries(voltage: float) -> float:
    if voltage >= 3.00:
        return 100
    if 2.80 <= voltage < 3.00:
        return _interpolate(
            voltage=voltage, voltage_range=(2.80, 3.00), percentage_range=(81, 100)
        )
    if 2.60 <= voltage < 2.80:
        return _interpolate(
            voltage=voltage, voltage_range=(2.60, 2.80), percentage_range=(53, 81)
        )
    if 2.50 <= voltage < 2.60:
        return _interpolate(
            voltage=voltage, voltage_range=(2.50, 2.60), percentage_range=(28, 53)
        )
    if 2.20 <= voltage < 2.50:
        return _interpolate(
            voltage=voltage, voltage_range=(2.20, 2.50), percentage_range=(5, 28)
        )
    if 2.10 <= voltage < 2.20:
        return _interpolate(
            voltage=voltage, voltage_range=(2.10, 2.20), percentage_range=(0, 5)
        )
    return 0


def _interpolate(
        voltage: float,
        voltage_range: tuple[float, float],
        percentage_range: tuple[int, int],
) -> float:
    return (voltage - voltage_range[0]) / (voltage_range[1] - voltage_range[0]) * (
            percentage_range[1] - percentage_range[0]
    ) + percentage_range[0]
