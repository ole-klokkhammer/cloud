#!/bin/bash

set -e 

export LOG_LEVEL=INFO
export SNAPSHOT_DIR=../snapshots
export LOCAL_DEBUG=1
export KAFKA_TOPIC=camera_frames
export KAFKA_BOOTSTRAP_SERVERS=kafka-kafka-bootstrap.kafka:9092

source venv/bin/activate 
python app/main.py