#
https://vikunja.io/docs/full-docker-example/

## Setup database
* CREATE DATABASE vikunja;
* CREATE USER vikunja WITH PASSWORD 'xxx';
* GRANT ALL ON DATABASE vikunja TO vikunja;
* GRANT ALL PRIVILEGES ON SCHEMA public TO vikunja; 
* ALTER SCHEMA public OWNER TO vikunja;

## setup volume 
* sudo zfs create -o quota=500M k3s/vikunja-data  
* sudo zfs list -o name,volsize,used,available k3s/vikunja-data

## setup 
* kubectl create secret generic -n apps  vikunja-secrets --from-env-file=.env 
* kubectl create -f ./storage.yaml
* kubectl create -f ./deployment.yaml
* kubectl create -f ./service.yaml

### update env
* kubectl create secret generic -n vikunja vikunja-secrets --from-env-file=.env --dry-run=client -o yaml | kubectl apply -f -

## Keycloak integration
* https://vikunja.io/docs/openid-example-configurations/
* https://vikunja.io/docs/openid/#setup-in-keycloak
* FIXME: currently needs :unstable tag to be able to populate provider list
 
## Admin user

The first user to register (either via local or Keycloak login) becomes the Vikunja admin by default.