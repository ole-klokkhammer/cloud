# zigbee2mqtt
* https://github.com/stanvn/zigbee-plant-sensor?tab=readme-ov-file
* https://www.hackster.io/rbaron/b-parasite-an-open-source-ble-soil-moisture-sensor-006441

## info
* https://support.electrolama.com/radio-docs/zigbee2mqtt/
* https://www.zigbee2mqtt.io/guide/configuration/adapter-settings.html

## setup volume
Use volumeMode: Block for ZVOLs
Use volumeMode: Filesystem for datasets 

* sudo zfs create -o quota=500M k3s/zigbee2mqtt-data  
* sudo zfs list -o name,volsize,used,available k3s/homeassistant-data

## setup
