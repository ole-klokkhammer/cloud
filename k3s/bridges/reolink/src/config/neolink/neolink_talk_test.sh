#!/usr/bin/env bash

set -e

ffmpeg -i https://rhasspy.github.io/piper-samples/samples/en/en_US/lessac/high/speaker_0.mp3 -f  alaw -ar 8000 -f wav - | /config/neolink/neolink talk Entrance -c /config/neolink/neolink.toml --volume=0.7 -m -i "fdsrc fd=0"
