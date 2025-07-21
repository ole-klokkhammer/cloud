# cam2mqtt
https://github.com/berfenger/cam2mqtt/blob/main/README.md

## setup
* kubectl create secret generic cam2mqtt-config \
  --from-file=config.yml=./secrets/config.yml \
  -n bridges