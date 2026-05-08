# cam2mqtt
https://github.com/berfenger/cam2mqtt/blob/main/README.md

## setup
* kubectl create secret generic -n bridges  cam2mqtt-secrets --from-env-file=.env
* kubectl apply -f config.yaml