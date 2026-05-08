#!/usr/bin/python3
import binascii 
import logging
from paho.mqtt import MQTTException, publish
import archive.k3s.bridges.bluetooth2amqp.src.app.env as env 

def bytes_as_str(value: bytes) -> str:
    return binascii.b2a_hex(value).decode('utf-8', errors='ignore')

 