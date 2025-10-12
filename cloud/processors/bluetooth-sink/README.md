# sensor

* kubectl create secret generic bluetooth-sink-config --from-env-file=./src/.env -n processors


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

#### airthings connect
CREATE TABLE IF NOT EXISTS bluetooth.airthings_device (
    id SERIAL,
    timestamp TIMESTAMPTZ DEFAULT now(),
    serial INTEGER NOT NULL,
    model_number INTEGER NOT NULL,
    mac VARCHAR(100) NOT NULL,
    manufacturer_name VARCHAR(100),
    hardware_revision VARCHAR(100),
    firmware_revision VARCHAR(100),
    location_id TEXT,
    PRIMARY KEY (id, timestamp)
);
SELECT create_hypertable('bluetooth.airthings_device', 'timestamp');

CREATE TABLE IF NOT EXISTS bluetooth.airthings_data (
    id SERIAL,
    timestamp TIMESTAMPTZ DEFAULT now(),
    serial INTEGER NOT NULL, 
    temperature DOUBLE PRECISION,
    humidity DOUBLE PRECISION,
    co2 DOUBLE PRECISION,
    voc DOUBLE PRECISION, 
    radon_1_day_average DOUBLE PRECISION,
    radon_long_term_average DOUBLE PRECISION,
    pressure DOUBLE PRECISION
);
SELECT create_hypertable('bluetooth.airthings_data', 'timestamp');


CREATE TABLE IF NOT EXISTS bluetooth.airthings_battery (
    id SERIAL,
    timestamp TIMESTAMPTZ DEFAULT now(),
    serial INTEGER NOT NULL, 
    battery_level DOUBLE PRECISION,
    voltage DOUBLE PRECISION
);
SELECT create_hypertable('bluetooth.airthings_battery', 'timestamp');