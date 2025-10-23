#!/usr/bin/python3
import binascii 
import logging
from paho.mqtt import MQTTException, publish
import env 

def bytes_as_str(value: bytes) -> str:
    return binascii.b2a_hex(value).decode('utf-8', errors='ignore')

 