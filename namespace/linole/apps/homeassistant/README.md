# Setup database 
* CREATE DATABASE homeassistant;
* CREATE USER homeassistant WITH PASSWORD 'xxxx';
* GRANT ALL ON DATABASE homeassistant TO homeassistant;
* GRANT ALL PRIVILEGES  ON SCHEMA public TO homeassistant;

# Apply kube 
* kubectl create -f ./deployment.yaml
* kubectl create -f ./service.yaml

https://github.com/freol35241/ltss


# restore longhorn backup volume
- create the volume in longhorn
- create a volume in kubernetes
- select the volume in volumeClaimTemplates with volumeName: homeassistant-data