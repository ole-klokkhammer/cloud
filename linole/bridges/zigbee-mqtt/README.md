#
* kubectl create configmap zigbee2mqtt-config --from-file=./config -n linole 
* kubectl create -f ./deployment.yaml
* kubectl create -f ./service.yaml
* kubectl cp ./config/configuration.yaml mqtt/zigbee2mqtt-0:/app/data/configuration.yaml
* kubectl cp ./config/coordinator_backup.json mqtt/zigbee2mqtt-0:/app/data/coordinator_backup.json
* kubectl cp ./config/database.db mqtt/zigbee2mqtt-0:/app/data/database.db
* kubectl cp ./config/state.json mqtt/zigbee2mqtt-0:/app/data/state.json


# Extensions
* kubectl cp ./config/app/data/extension/livingroom-switch.js mqtt/zigbee2mqtt-0:/app/data/extension/livingroom-switch.js
* restart from ui: settings -> tools


# binding
* zigbee2mqtt/bridge/request/device/bind
  {"from": "garden_switch", "to": "garden"}

# unbind
* zigbee2mqtt/bridge/request/device/unbind
  {"from": "garden_switch", "to": "garden"}