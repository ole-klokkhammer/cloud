#!/usr/bin/env bash

set -ex

echo "test log" | tee /tmp/neolink_talk.log

ffmpeg -fflags nobuffer -rtsp_transport tcp -i rtsp://127.0.0.1:8554/incoming -acodec pcm_alaw -ar 8000 -ac 1 -f wav - | /config/neolink/neolink talk Entrance -c /config/neolink/neolink.toml --volume=1.0 -m -i "fdsrc fd=0" 2>&1 | tee /tmp/neolink_talk.log
# ffmpeg -fflags nobuffer -f alsa -i default -acodec pcm_alaw -ar 8000 -ac 1 -f rtsp -rtsp_transport tcp rtsp://127.0.0.1:8554/incoming