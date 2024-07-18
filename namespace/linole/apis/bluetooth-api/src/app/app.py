#!/usr/bin/python3

import waitress

from flask import Flask
from flask_restful import Resource, Api
from resources.airthings import Airthings
from resources.paxcalima import PaxCalima
from resources.oralb import OralB

app = Flask(__name__)
api = Api(app)


class DefaultResource(Resource):
    def get(self):
        return True


api.add_resource(DefaultResource, '/')
api.add_resource(Airthings, '/airthings')
api.add_resource(PaxCalima, '/paxcalima')
api.add_resource(OralB, '/oralb')

if __name__ == '__main__':
    waitress.serve(app)
