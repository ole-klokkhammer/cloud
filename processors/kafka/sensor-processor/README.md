# sensor

* kubectl create secret generic sensor-processor-config --from-env-file=./app/.env -n kafka-processors


## database setup

-- Create a new user for the current app
CREATE USER sensor_processor WITH PASSWORD 'securepassword';


CREATE SCHEMA sensor;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA sensor TO sensor_processor;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA sensor TO sensor_processor;   


### database tables 
CREATE TABLE IF NOT EXISTS sensor.airthings (
    id SERIAL,
    timestamp TIMESTAMPTZ DEFAULT now(),
    name VARCHAR(100) NOT NULL,
    pin VARCHAR(100) NOT NULL,
    mac VARCHAR(100),
    temperature DOUBLE PRECISION,
    humidity DOUBLE PRECISION,
    co2 DOUBLE PRECISION,
    voc DOUBLE PRECISION,
    pm25 DOUBLE PRECISION,
    radon DOUBLE PRECISION,
    pressure DOUBLE PRECISION,
    raw_data JSONB NOT NULL
); 
SELECT create_hypertable('sensor.airthings', 'timestamp');