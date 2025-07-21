#!/bin/bash

if [ -z "$1" ]; then
  echo "Usage: $0 <camera_name>"
  exit 1
fi

CAMERA_NAME=$1 
REMOTE_USER=ubuntu
REMOTE_HOST=192.168.10.2
REMOTE_DIR="/mnt/data/camera/${CAMERA_NAME}/video"
LOCAL_DIR="/home/ole/Downloads/camera/${CAMERA_NAME}"
RETRIEVAL_COUNT=10000

# Get the last $RETRIEVAL_COUNT files and sync them
ssh ${REMOTE_USER}@${REMOTE_HOST} "ls -tp ${REMOTE_DIR} | grep -v / | head -${RETRIEVAL_COUNT}" > /tmp/snapshot_files.txt

rsync -av --files-from=/tmp/snapshot_files.txt --no-relative "${REMOTE_USER}@${REMOTE_HOST}:${REMOTE_DIR}/" "${LOCAL_DIR}/"