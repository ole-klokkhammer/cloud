# Setup database 
* CREATE DATABASE homeassistant;
* CREATE USER homeassistant WITH PASSWORD 'xxxx';
* GRANT ALL ON DATABASE homeassistant TO homeassistant;

# Apply kube 
* kubectl create -f ./deployment.yaml
* kubectl create -f ./service.yaml

https://github.com/freol35241/ltss

GRANT ALL PRIVILEGES  ON SCHEMA public TO homeassistant;


kubectl cp ./config mqtt/homeassistant-0:/