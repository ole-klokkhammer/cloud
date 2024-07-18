import paho.mqtt.client as mqtt
import requests
from os import getenv

HOMEASSISTANT_TOKEN = getenv('HOMEASSISTANT_TOKEN', '')
HOST = getenv('HOST', '192.168.0.201')
PORT = getenv('PORT', 1883)
KEEPALIVE = getenv('KEEPALIVE', 60)

print("Starting up ...")


def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    client.subscribe("diun/#")


def on_message(client, userdata, msg):
    try:
        print(f"`{msg.payload.decode()}` from `{msg.topic}` topic")
        data = {
            'message': f"`{msg.payload.decode()}`",
            'title': 'New docker version',
            'target': []
        }
        headers = {
            'Authorization': 'Bearer ' + HOMEASSISTANT_TOKEN
        }
        res = requests.post(
            'http://homeassistant.linole:6102/api/services/notify/mobile_app_pixel_5',
            json=data,
            headers=headers
        )
        print(res.status_code)
    except Exception as e:
        print(e)


client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect(HOST, PORT, KEEPALIVE)

# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface.
client.loop_forever()
