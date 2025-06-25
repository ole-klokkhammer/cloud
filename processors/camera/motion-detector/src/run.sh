#!/bin/bash

set -e

export LOG_LEVEL=DEBUG
export LOCAL_DEBUG=1
export KAFKA_BOOTSTRAP_SERVERS=192.168.10.201:9092
# export ENTRANCE_ROOF_STREAM_URL=rtsp://192.168.10.208:8554/entrance_roof
export ENTRANCE_ROOF_STREAM_URL=rtsp://192.168.10.208:8554/office_test
source venv/bin/activate 
python app/main.py