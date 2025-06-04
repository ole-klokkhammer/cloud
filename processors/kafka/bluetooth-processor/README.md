# sensor

* kubectl create secret generic bluetooth-processor-config --from-env-file=./src/.env -n kafka-processors


## database setup

-- Create a new user for the current app
CREATE USER bluetooth_processor WITH PASSWORD 'securepassword';


CREATE SCHEMA bluetooth;
GRANT USAGE ON SCHEMA bluetooth TO bluetooth_processor;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA bluetooth TO bluetooth_processor;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA bluetooth TO bluetooth_processor;   


### database tables 

#### scan
CREATE TABLE bluetooth.scan (
    id SERIAL,
    timestamp TIMESTAMPTZ DEFAULT now(),
    name TEXT,
    address TEXT NOT NULL,
    rssi INTEGER,
    manufacturer_data JSONB
);
SELECT create_hypertable('bluetooth.scan', 'timestamp');

#### connect
CREATE TABLE bluetooth.connect (
    id SERIAL,
    timestamp TIMESTAMPTZ DEFAULT now(),
    address TEXT NOT NULL,
    raw JSONB
);
SELECT create_hypertable('bluetooth.connect', 'timestamp');