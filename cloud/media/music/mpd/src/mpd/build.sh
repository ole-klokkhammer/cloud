#!/bin/bash

set -euxo pipefail  

export MPD_VERSION=0.24.5

echo "Building MPD version $MPD_VERSION"


docker buildx create --use
docker buildx build \
  -f Dockerfile \
  --platform linux/amd64 \
  --build-arg MPD_VERSION=$MPD_VERSION \
  -t ghcr.io/ole-klokkhammer/mpd:$MPD_VERSION \
  --push .