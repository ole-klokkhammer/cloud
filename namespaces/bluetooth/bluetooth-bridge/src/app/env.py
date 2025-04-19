#!/usr/bin/python3
import os

mqtt_broker = os.getenv("MQTT_BROKER", "192.168.10.207")   
mqtt_port = int(os.getenv("MQTT_PORT", 1883))  # Default to 1883 if not set
mqtt_client_id = os.getenv("MQTT_CLIENT_ID", "bluetooth_bridge")  # Default to "bluetooth_bridge" if not set

# airthings
airthings_wave_plus_basement = os.getenv("AIRTHINGS_WAVE_PLUS_BASEMENT", "F4:60:77:6D:33:C0")
airthings_wave_plus_living_room = os.getenv("AIRTHINGS_WAVE_PLUS_LIVING_ROOM", "F4:60:77:70:58:EA")
airthings_wave_plus_bedroom = os.getenv("AIRTHINGS_WAVE_PLUS_BEDROOM", "A4:DA:32:28:C4:2F")