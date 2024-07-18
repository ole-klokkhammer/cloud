import logging

from bluepy.btle import UUID, Peripheral
import struct
import math
from flask_restful import Resource, reqparse

CHARACTERISTIC_PIN_CODE = "4cad343a-209a-40b7-b911-4d9b3df569b2"
CHARACTERISTIC_SENSOR_DATA = "528b80e8-c47a-4c0a-bdf1-916a7748f412"


class Calima():

    def __init__(self, mac, pin):
        self.periph = None
        self.mac = mac
        self.pin = pin

    def connect(self):
        if self.periph is None:
            self.periph = Peripheral(self.mac)
        logging.info("Connecting ...")
        pkg = struct.pack("<I", int(self.pin))
        self.get_characteristics(CHARACTERISTIC_PIN_CODE).write(pkg, withResponse=True)

    def disconnect(self):
        if self.periph is not None:
            self.periph.disconnect()
            self.periph = None

    def get_sensor_data(self):
        logging.info("Reading sensor data ...")
        rawData = self.get_characteristics(CHARACTERISTIC_SENSOR_DATA).read()
        rawData = struct.unpack('<4HBHB', rawData)

        humidity = round(math.log2(rawData[0]) * 10, 2) if rawData[0] > 0 else 0
        temperature = rawData[1] / 4
        light = rawData[2]
        fan_speed = rawData[3]

        mode = "No trigger"
        if ((rawData[4] >> 4) & 1) == 1:
            mode = "Boost"
        elif (rawData[4] & 3) == 1:
            mode = "Trickle ventilation"
        elif (rawData[4] & 3) == 2:
            mode = "Light ventilation"
        elif (rawData[4] & 3) == 3:
            mode = "Humidity ventilation"

        data = [
            humidity,
            temperature,
            light,
            fan_speed,
            mode
        ]
        return data

    def get_characteristics(self, uuid):
        return self.periph.getCharacteristics(uuid=uuid)[0]


def read_values(mac, pin):
    try:
        pycalima = Calima(mac, pin)
        pycalima.connect()
        sensors = pycalima.get_sensor_data()
        pycalima.disconnect()
        logging.info(sensors)
        return sensors
    except Exception as e:
        print(e)
        return


class PaxCalima(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('mac', type=str)
        self.reqparse.add_argument('pin', type=int)

    def get(self):
        args = self.reqparse.parse_args()
        logging.info(args)
        return read_values(args['mac'], args['pin'])
