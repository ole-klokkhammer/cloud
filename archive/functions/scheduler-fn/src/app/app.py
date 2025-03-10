import logging

import paho.mqtt.client as mqtt
import requests
from os import getenv
import schedule
import time

MQTT_HOST = getenv('HOST')
MQTT_PORT = getenv('PORT', 1883)
MQTT_KEEPALIVE = getenv('KEEPALIVE', 60)
MQTT_CLIENT_ID = getenv('CLIENT_ID', 'scheduler-fn')
BLUETOOTH_API_URL = getenv('BLUETOOTH_API_URL', 'http://bluetooth-api.linole:8000')


def on_connect(client, userdata, flags, reason_code, properties):
    logging.info(f"Connected with result code {reason_code}")


def on_disconnect(client, userdata, flags, reason_code, properties):
    logging.info(f"Disconnected with result code {reason_code}")


client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.on_connect = on_connect
client.on_disconnect = on_disconnect
client.connect(MQTT_HOST, MQTT_PORT)
client.loop_start()


def airthings():
    try:
        response = requests.get(BLUETOOTH_API_URL + '/airthings?pin=2930018919')
        data = response.json()
        client.publish('bluetooth/airthings', payload=str(data), qos=2, retain=True)
        client.publish('bluetooth/airthings/co2', payload=str(data['co2']), qos=2, retain=True)
        client.publish('bluetooth/airthings/temperature', payload=str(data['temperature']), qos=2, retain=True)
        client.publish('bluetooth/airthings/voc', payload=str(data['voc']), qos=2, retain=True)
        client.publish('bluetooth/airthings/humidity', payload=str(data['humidity']), qos=2, retain=True)
        client.publish('bluetooth/airthings/pressure', payload=str(data['pressure']), qos=2, retain=True)
        client.publish('bluetooth/airthings/radon_lt_avg', payload=str(data['radon_lt_avg']), qos=2, retain=True)
        client.publish('bluetooth/airthings/radon_st_avg', payload=str(data['radon_st_avg']), qos=2, retain=True)
    except Exception as e:
        logging.error(e)


def oralb():
    try:
        response = requests.get(BLUETOOTH_API_URL + '/oralb?mac=10:CE:A9:2A:41:F6')
        data = response.json()
        client.publish('bluetooth/oralb', payload=str(data), qos=2, retain=True)
    except Exception as e:
        logging.error(e)


def paxcalima():
    try:
        response = requests.get(BLUETOOTH_API_URL + '/paxcalima?mac=58:2B:DB:34:21:4D&pin=33394119')
        data = response.json()
        client.publish('bluetooth/paxcalima', payload=str(data), qos=2, retain=True)
    except Exception as e:
        logging.error(e)


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logging.info("Scheduling jobs ...")

schedule.every(15).minutes.do(airthings)
# schedule.every(1).minutes.do(oralb)
# schedule.every(5).minutes.do(paxcalima)

while True:
    schedule.run_pending()
    time.sleep(1)
