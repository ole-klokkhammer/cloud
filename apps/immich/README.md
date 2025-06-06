# immich
* https://immich.app/docs/overview/welcome/
* https://immich.app/docs/administration/postgres-standalone

## existing postgres setup 
see postgres extension setup. we need vector and vectorchord

### upgrading vectorchord extension
* update files mounted on postgres, then:
* ALTER EXTENSION vchord UPDATE;

## create database
* CREATE DATABASE immich;
* CREATE USER immich_admin WITH PASSWORD 'securepassword';
* CREATE EXTENSION vchord CASCADE;
* CREATE EXTENSION earthdistance CASCADE;


CREATE SCHEMA bluetooth;
GRANT USAGE ON SCHEMA bluetooth TO bluetooth_processor;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA bluetooth TO bluetooth_processor;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA bluetooth TO bluetooth_processor;   

## setup
* kubectl create namespace immich
* 