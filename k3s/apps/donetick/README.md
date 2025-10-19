# donetick

https://docs.donetick.com/getting-started/


## Setup database
* CREATE DATABASE donetick;
* CREATE USER donetick WITH PASSWORD 'xxx';
* GRANT ALL ON DATABASE donetick TO donetick;
* GRANT ALL PRIVILEGES ON SCHEMA public TO vikunja; 
* ALTER SCHEMA public OWNER TO vikunja;

## deploy
* kubectl create secret generic -n apps  donetick-secrets --from-env-file=.env 
* kubectl apply -f deployment.yaml

## pfsense haproxy
