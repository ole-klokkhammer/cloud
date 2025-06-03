# sensor

* kubectl create secret generic sensor-processor-config --from-env-file=./app/.env -n kafka-processors


## database

-- Create a new database for sensordb
CREATE DATABASE sensordb;

-- Create a new user for sensordb
CREATE USER sensordb_writer WITH PASSWORD 'securepassword';

-- Grant privileges to the new user on the Keycloak database
GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE sensor TO sensordb_writer;

-- Grant privileges to the sequence used by the SERIAL id column
GRANT USAGE, SELECT ON SEQUENCE sensor_id_seq TO sensordb_writer;

CREATE TABLE IF NOT EXISTS sensor (
    id SERIAL PRIMARY KEY,
    data JSONB NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now()
);