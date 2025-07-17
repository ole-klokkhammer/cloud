#!/bin/bash

set -e

APP_NAME="llama-api"

# Step 1: Auto-bump the patch version
PREV_VERSION=$(grep -m1 -oP 'ole-klokkhammer/'"$APP_NAME"':\K[0-9]+\.[0-9]+\.[0-9]+' deployment.yaml)
IFS='.' read -r major minor patch <<< "$PREV_VERSION"
NEW_VERSION="$major.$minor.$((patch + 1))"

echo "$PREV_VERSION" 

# Step 2: Update the Docker image version in the Kubernetes deployment configuration
sed -i "s#ghcr.io/ole-klokkhammer/$APP_NAME:$PREV_VERSION#ghcr.io/ole-klokkhammer/$APP_NAME:$NEW_VERSION#g" deployment.yaml

# Step 3: Build and push the new Docker image
cd src && docker buildx build --target server --push --platform linux/amd64 -t "ghcr.io/ole-klokkhammer/$APP_NAME:$NEW_VERSION" .

cd .. && kubectl apply -f deployment.yaml