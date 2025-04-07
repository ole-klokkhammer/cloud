#!/usr/bin/python3

import logging
import uuid

from quart import Quart, jsonify, request

import resources.bluetooth as bluetooth
import resources.airthings as airthings
from resources import utils

logging.basicConfig(level=logging.INFO)
logging.info("Starting Bluetooth API")
app = Quart(__name__)


@app.route('/bluetooth/scan')
async def bluetooth_scan():
    timeout = request.args.get('timeout', default=5, type=int)
    device_list = await bluetooth.scan(timeout)
    return jsonify(device_list)


@app.route('/bluetooth/<address>', methods=['GET'])
async def bluetooth_connect(address: str):
    device_list = await bluetooth.connect(address)
    return jsonify(device_list)


@app.route('/bluetooth/<address>/<characteristic>', methods=['GET'])
async def bluetooth_read_characteristics(address: str, characteristic: uuid.UUID):
    command_hex = request.args.get('command_hex', type=str)
    format_type = request.args.get('format_type', type=str)
    response = await bluetooth.send_command(
        address=address,
        characteristic=characteristic,
        command=bytearray.fromhex(command_hex),
        format_type=format_type,
    )
    return jsonify(utils.hex_bytes_as_str(response))


@app.route('/airthings/<address>', methods=['GET'])
async def airthings_waveplus_read_sensor_data(address: str):
    response = await airthings.wave_plus_read_sensor_data(address)
    return jsonify(response)


@app.route('/airthings/<address>/battery', methods=['GET'])
async def airthings_waveplus_read_battery(address: str):
    value = await airthings.read_wave_plus_battery(address)
    return jsonify(value)


@app.route('/airthings/parse/manufacturer-data', methods=['GET'])
async def airthings_waveplus_parse_pin_from_manufacturer_data():
    hex_value = request.args.get('hex_value', type=str)
    return jsonify(airthings.wave_plus_manufacturer_data(bytearray.fromhex(hex_value)))


@app.route('/airthings/parse/sensor-data', methods=['GET'])
async def airthings_waveplus_parse_sensor_data():
    hex_value = request.args.get('hex_value', type=str)
    return jsonify(airthings.wave_plus_sensor_data(bytearray.fromhex(hex_value)))


app.run()
