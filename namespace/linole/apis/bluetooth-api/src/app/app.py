#!/usr/bin/python3

import waitress
import logging
import os
import traceback
from flask import Flask, request
from flask_restful import Resource, Api
from resources.airthings import Airthings
from resources.paxcalima import PaxCalima
from resources.oralb import OralB

logging.basicConfig(level=logging.DEBUG)
logging.info("Starting Bluetooth API")
app = Flask(__name__)

@app.errorhandler(Exception)
def handle_exception(e):
    logging.error("An error occurred: %s", str(e))
    logging.error(traceback.format_exc())
    return {"error": str(e) }, 500

api = Api(app)
api.add_resource(Airthings, '/airthings')
api.add_resource(PaxCalima, '/paxcalima')
api.add_resource(OralB, '/oralb')

if __name__ == '__main__':
    waitress.serve(app, port=int(os.getenv('FLASK_PORT', 8080)))
