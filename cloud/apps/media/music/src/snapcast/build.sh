#!/bin/bash

set -euxo pipefail

export SNAPCAST_VERSION=0.32.3

echo "Building Snapcast version $SNAPCAST_VERSION"

# build server image
docker buildx build \
  -f Dockerfile.server \
  --platform linux/amd64 \
  --build-arg SNAPCAST_VERSION=$SNAPCAST_VERSION \
  -t ghcr.io/ole-klokkhammer/snapserver:$SNAPCAST_VERSION \
  --push .

# build client image
docker buildx build \
  -f Dockerfile.client \
  --platform linux/amd64 \
  --build-arg SNAPCAST_VERSION=$SNAPCAST_VERSION \
  -t ghcr.io/ole-klokkhammer/snapclient:$SNAPCAST_VERSION \
  --push .