#!/bin/bash

set -e

export LOG_LEVEL=DEBUG
export LOCAL_DEBUG=1
export KAFKA_TOPIC=camera_frames_debug
export KAFKA_BOOTSTRAP_SERVERS=kafka-kafka-bootstrap.kafka:9092
# export ENTRANCE_ROOF_STREAM_URL=rtsp://go2rtc.camera-bridge:8554/entrance_roof
export ENTRANCE_ROOF_STREAM_URL=rtsp://go2rtc.camera-bridge:8554/office_test
source venv/bin/activate 
python app/main.py