# keycloak

* kubectl create namespace keycloak
* kubectl create secret generic keycloak-config --from-env-file=.env -n keycloak
* kubectl apply -f configmap.yaml
* kubectl apply -f service.yaml

## database

-- Create a new database for Keycloak
CREATE DATABASE keycloak;

-- Create a new user for Keycloak
CREATE USER keycloak WITH PASSWORD 'securepassword';

-- Grant privileges to the new user on the Keycloak database
GRANT ALL PRIVILEGES ON DATABASE keycloak TO keycloak;
GRANT USAGE ON SCHEMA public TO keycloak;
GRANT CREATE ON SCHEMA public TO keycloak;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO keycloak;

## deploy

* kubectl apply -f deployment.yaml

## ssl termination behind proxy

### pfsense

* X-Forwarded-For:%ci
* X-Forwarded-Host:%[ssl_fc_sni]

### keycloak

env:
* name: KC_PROXY
  value: "edge"
* name: KC_HOSTNAME
  valueFrom:
    secretKeyRef:
      name: keycloak-config
      key: KC_HOSTNAME
* name: KC_HTTP_ENABLED
  value: "true"
