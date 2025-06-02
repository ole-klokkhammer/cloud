#!/bin/bash

APP_NAME="bluetooth-mqtt"

# Step 1: Auto-bump the patch version
PREV_VERSION=$(grep -oP 'olklokk/'"$APP_NAME"':\K[0-9]+\.[0-9]+\.[0-9]+' deployment.yaml)
IFS='.' read -r major minor patch <<< "$PREV_VERSION"
NEW_VERSION="$major.$minor.$((patch + 1))"

# Step 2: Update the Docker image version in the Kubernetes deployment configuration
sed -i "s/olklokk\/$APP_NAME:$PREV_VERSION/olklokk\/$APP_NAME:$NEW_VERSION/g" deployment.yaml

# Step 3: Build and push the new Docker image
cd src && docker buildx build --push --platform linux/amd64 -t "olklokk/$APP_NAME:$NEW_VERSION" .

cd .. && kubectl apply -f deployment.yaml