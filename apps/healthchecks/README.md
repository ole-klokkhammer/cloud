# healthchecks
https://github.com/healthchecks/healthchecks

## items
* etcd-backups on host
* postgres-backups on host


## setup
## database

-- Create a new database for healthchecks
CREATE DATABASE healthchecks;

-- Create a new user for healthchecks
CREATE USER healthchecks WITH PASSWORD '';

-- Grant privileges to the new user on the healthchecks database
GRANT ALL PRIVILEGES ON DATABASE healthchecks TO healthchecks;
GRANT USAGE ON SCHEMA public TO healthchecks;
GRANT CREATE ON SCHEMA public TO healthchecks;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO healthchecks;

## kubernetes
* kubectl create namespace healthchecks
* kubectl create secret generic -n healthchecks  healthchecks-secrets --from-env-file=.env
* kubectl apply -f deployment.yaml
* enter pod, then:
    * manage.py migrate # create tables
    * manage.py createsuperuser
  
