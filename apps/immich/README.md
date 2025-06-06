# immich
* https://immich.app/docs/overview/welcome/
* https://immich.app/docs/administration/postgres-standalone

## known issues in kubernetes
* DNS in Alpine containers: https://immich.app/docs/install/kubernetes

## existing postgres setup 
see postgres extension setup. we need vector and vectorchord

### upgrading vectorchord extension
* update files mounted on postgres, then:
* ALTER EXTENSION vchord UPDATE;

## create database
* CREATE DATABASE immich;
* CREATE USER immich_admin WITH PASSWORD 'securepassword';
* ALTER DATABASE immich OWNER TO immich_admin;
* CREATE EXTENSION vchord CASCADE;
* CREATE EXTENSION earthdistance CASCADE;
  

## setup
* kubectl create namespace immich
* kubectl create secret generic -n immich  immich-secrets --from-env-file=.env
* kubectl apply -f storage.yaml
* kubectl apply -f deployment.yaml
* kubectl apply -f service.yaml

## oauth (keycloak)
https://immich.app/docs/administration/oauth