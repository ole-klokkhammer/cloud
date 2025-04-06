#!/usr/bin/python3
import struct
from datetime import datetime


# https://github.com/Airthings/airthings-ble/blob/main/airthings_ble/const.py

def parse_pin_from_manufacturer_data(manu_data_hex_str: str):
    if not manu_data_hex_str or manu_data_hex_str == "None":
        return None
    value = bytearray.fromhex(manu_data_hex_str)
    return value[0] | (value[1] << 8) | (value[2] << 16) | (value[3] << 24)


def sensor_data(raw_data: bytearray) -> dict[str, float | None | str]:
    name = "Plus"
    format_type = "<4B8H"
    scale = 0
    vals = _decode_base(name, format_type, scale, raw_data)
    val = vals[name]

    data: dict[str, float | None | str] = {}
    data["date_time"] = str(datetime.isoformat(datetime.now()))
    data["humidity"] = val[1] / 2.0
    # data["illuminance"] = illuminance_converter(value=val[2])
    data["radon_1day_avg"] = val[4]
    data["radon_longterm_avg"] = val[5]
    data["temperature"] = val[6] / 100.0
    data["pressure"] = val[7] / 50.0
    data["co2"] = val[8] * 1.0
    data["voc"] = val[9] * 1.0
    return data


def _decode_base(name, format_type, scale, raw_data: bytearray) -> dict[str, tuple[float, ...]]:
    val = struct.unpack(format_type, raw_data)
    if len(val) == 1:
        res = val[0] * scale
    else:
        res = val
    return {name: res}
