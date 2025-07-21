#!/usr/bin/python3
import os

log_level = os.getenv("LOG_LEVEL") 
kafka_broker = os.getenv("KAFKA_BROKER")    
bluetooth_scan_cron = os.getenv("CRON_GENERIC_BLE_SCAN")

# airthings
airthings_wave_plus_sensor_data_cron = os.getenv("CRON_AIRTHINGS_WAVE_PLUS_SENSOR_DATA")
airthings_wave_plus_battery_cron = os.getenv("CRON_AIRTHINGS_WAVE_PLUS_BATTERY")
 

airthings_wave_plus_basement = os.getenv("AIRTHINGS_WAVE_PLUS_BASEMENT", "F4:60:77:6D:33:C0")
airthings_wave_plus_living_room = os.getenv("AIRTHINGS_WAVE_PLUS_LIVING_ROOM", "F4:60:77:70:58:EA")
airthings_wave_plus_bedroom = os.getenv("AIRTHINGS_WAVE_PLUS_BEDROOM", "A4:DA:32:28:C4:2F")