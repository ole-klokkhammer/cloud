
import json
import logging 
from paho.mqtt import MQTTException, publish
import airthings.device
import env
import airthings

async def read_sensor_data(device_id, name):
    try:
        response = await airthings.device.read_wave_plus_read_sensor_data(device_id)
        logging.debug(f"Result: {response}")
        publish.single(
            "bluetooth/airthings/" + name, 
            payload=json.dumps(response.__dict__), 
            hostname=env.mqtt_broker, 
            port=env.mqtt_port,
            client_id=env.mqtt_client_id,
        ) 
    except MQTTException as e:
        logging.error(f"Failed to publish to MQTT: {e}")
    except Exception as e:
        logging.error(f"Unexpected error publishing to MQTT: {e}")


async def wave_plus_sensor_data_basement_task():  
    read_sensor_data( env.airthings_wave_plus_basement, "basement")
    

async def wave_plus_sensor_data_livingroom_task(): 
    read_sensor_data( env.airthings_wave_plus_living_room, "living_room") 

async def wave_plus_sensor_data_bedroom_task(): 
    read_sensor_data( env.airthings_wave_plus_bedroom, "bedroom")