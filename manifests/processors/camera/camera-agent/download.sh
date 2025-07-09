#!/bin/bash

REMOTE_USER=ubuntu
REMOTE_HOST=192.168.10.2
REMOTE_DIR=/mnt/data/camera/entrance_hallway/video
LOCAL_DIR=/home/ole/Downloads/camera/entrance_hallway
RETRIEVAL_COUNT=10000

# Get the last $RETRIEVAL_COUNT files and sync them
ssh ${REMOTE_USER}@${REMOTE_HOST} "ls -tp ${REMOTE_DIR} | grep -v / | head -${RETRIEVAL_COUNT}" > /tmp/snapshot_files.txt

rsync -av --files-from=/tmp/snapshot_files.txt --no-relative "${REMOTE_USER}@${REMOTE_HOST}:${REMOTE_DIR}/" "${LOCAL_DIR}/"