#!/bin/bash

export SNAPCAST_VERSION=0.32.3

# set AUDIO_GID and run with custom host/device/name
AUDIO_GID=$(getent group audio | cut -d: -f3)
docker run --rm --net=host --device /dev/snd \
  --entrypoint /bin/sh \
  ghcr.io/ole-klokkhammer/snapclient:${SNAPCAST_VERSION} \
  -c "snapclient tcp://192.168.10.218:1704"