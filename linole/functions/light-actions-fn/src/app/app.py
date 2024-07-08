import paho.mqtt.client as mqtt
import json
from os import getenv

DAY = 1
NIGHT = 2
HOST = getenv('HOST', '192.168.0.205')
PORT = getenv('PORT', 1883)
KEEPALIVE = getenv('KEEPALIVE', 60)

prevSunState = ''


def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    client.subscribe("homeassistant/sun/sun/state")


def on_message(client, userdata, msg):
    try:
        print(f"`{msg.payload.decode()}` from `{msg.topic}` topic")
        sunState = msg.payload.decode()

        global prevSunState
        if prevSunState != sunState:
            prevSunState = sunState
            if sunState in ['above_horizon']:
                data = {'scene_recall': DAY}
                client.publish('zigbee/all/set', payload=json.dumps(data), qos=2, retain=True)
                client.publish('zigbee/livingroom/set', payload=json.dumps(data), qos=2, retain=True)
            elif sunState in [f'below_horizon']:
                data = {'scene_recall': NIGHT}
                client.publish('zigbee/all/set', payload=json.dumps(data), qos=2, retain=True)
                client.publish('zigbee/livingroom/set', payload=json.dumps(data), qos=2, retain=True)
            else:
                print("No match")
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
