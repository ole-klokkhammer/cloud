# homeassistant

## Setup database
* CREATE DATABASE homeassistant;
* CREATE USER homeassistant WITH PASSWORD 'xxxx';
* GRANT ALL ON DATABASE homeassistant TO homeassistant;
* GRANT ALL PRIVILEGES  ON SCHEMA public TO homeassistant;

## setup volume
Use volumeMode: Block for ZVOLs
Use volumeMode: Filesystem for datasets 

* sudo zfs create -o quota=500M k3s/homeassistant-data  
* sudo zfs list -o name,volsize,used,available k3s/homeassistant-data

## setup
* kubectl create secret generic -n apps  homeassistant-secrets --from-env-file=.env
* kubectl create -f ./deployment.yaml
* kubectl create -f ./service.yaml

https://github.com/freol35241/ltss


# update configmap
* kubectl create configmap homeassistant-mqttsensors \
  --from-file=config/sensors/mqtt/ \
  -n apps \
  --dry-run=client -o yaml > homeassistant-mqttsensors.yaml

## webrtc
https://github.com/AlexxIT/WebRTC