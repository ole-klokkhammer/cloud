#!/bin/bash
 
export KAFKA_BOOTSTRAP_SERVERS=192.168.10.201:9092
export ENTRANCE_ROOF_STREAM_URL=rtsp://192.168.10.208:8554/entrance_roof
source venv/bin/activate 
python app/main.py