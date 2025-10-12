#
https://docs.donetick.com/getting-started/configration

## Setup database
* CREATE DATABASE donetick;
* CREATE USER donetick WITH PASSWORD 'xxx';
* select default database
* GRANT ALL ON DATABASE donetick TO donetick;
* GRANT ALL PRIVILEGES ON SCHEMA public TO donetick; 
* ALTER SCHEMA public OWNER TO donetick; 

## setup 
* kubectl create secret generic -n apps  donetick-secrets --from-env-file=.env   
* kubectl create -f ./deployment.yaml
* kubectl create -f ./service.yaml

### update env
* kubectl create secret generic -n donetick donetick-secrets --from-env-file=.env --dry-run=client -o yaml | kubectl apply -f -

## Keycloak integration
* https://docs.donetick.com/advance-settings/openid-connect-setup/ 
 