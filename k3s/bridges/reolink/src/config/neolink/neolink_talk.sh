#!/usr/bin/env bash

set -ex

echo "test log" | tee /tmp/neolink_talk.log

ffmpeg -fflags nobuffer -f alaw -ar 8000 -i - -f wav - | /config/neolink/neolink talk Entrance -c /config/neolink/neolink.toml --volume=1.0 -m -i "fdsrc fd=0" 2>&1 | tee /tmp/neolink_talk.log
# ffmpeg -fflags nobuffer -i - -ar 8000 -ac 1 -c:a pcm_alaw -f wav - | /config/neolink/neolink talk Entrance -c /config/neolink/neolink.toml --volume=1.0 -m -i "fdsrc fd=0" 2>&1 | tee /tmp/neolink_talk.log
