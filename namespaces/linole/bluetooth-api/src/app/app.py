#!/usr/bin/python3

import logging
from quart import Quart, jsonify, request

import resources.bluetooth as bluetooth
import resources.airthings as airthings

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


@app.route('/airthings/manufacturer/<manufacturer_id>', methods=['GET'])
async def airthings_parse_manufacturer_id(manufacturer_id: str):
    return jsonify(airthings.airthings_manufacturer_id(manufacturer_id))


@app.route('/airthings/sensor/<sensor_data>', methods=['GET'])
async def airthings_parse_sensor(sensor_data: str):
    return jsonify(airthings.sensor_data(bytearray.fromhex(sensor_data)))


app.run()
