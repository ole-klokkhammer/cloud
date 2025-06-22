# homeassistant

## Setup database
* CREATE DATABASE homeassistant;
* CREATE USER homeassistant WITH PASSWORD 'xxxx';
* GRANT ALL ON DATABASE homeassistant TO homeassistant;
* GRANT ALL PRIVILEGES  ON SCHEMA public TO homeassistant;

## setup
* kubectl create namespace homeassistant
* kubectl create secret generic -n homeassistant  homeassistant-secrets --from-env-file=.env
* kubectl create -f ./deployment.yaml
* kubectl create -f ./service.yaml

https://github.com/freol35241/ltss


# restore longhorn backup volume
- create the volume in longhorn
- create a volume in kubernetes
- select the volume in volumeClaimTemplates with volumeName: homeassistant-data

