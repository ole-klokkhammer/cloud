import logging

from bluepy.btle import Scanner, DefaultDelegate
from flask_restful import Resource, reqparse


class ScanDelegate(DefaultDelegate):
    def __init__(self):
        DefaultDelegate.__init__(self)

    def handleDiscovery(self, dev, isNewDev, isNewData):
        if isNewDev:
            logging.info("Discovered new device: %s" % dev.addr)


def searchmac(devices, mac):
    for dev in devices:
        if dev.addr == mac.lower():
            return dev
    return None


def read_values(mac):
    try:
        scanner = Scanner().withDelegate(ScanDelegate())
        devices = scanner.scan(5.0)
        device = searchmac(devices, mac)
        if device is None:
            return {
                'presence': 0
            }
        else:
            bytes_ = bytearray(bytes.fromhex(device.getValueText(255)))
            return {
                'presence': 1,
                'rssi': device.rssi,
                'running': bytes_[5],
                'pressure': bytes_[6],
                'time': bytes_[7] * 60 + bytes_[8],
                'mode': bytes_[9],
                'quadrant': bytes_[10]
            }
    except Exception as e:
        logging.error(e)
        return


class OralB(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('mac', type=str)

    def get(self):
        args = self.reqparse.parse_args()
        logging.info(args)
        return read_values(args['mac'])
