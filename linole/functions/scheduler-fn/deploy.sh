#!/bin/bash

APP_NAME="scheduler"

# Step 1: Define the new version
PREV_VERSION="1.0.5"
NEW_VERSION="1.0.6"

# Step 2: Update the Docker image version in the Kubernetes deployment configuration
sed -i "s/olklokk\/$APP_NAME:$PREV_VERSION/olklokk\/$APP_NAME:$NEW_VERSION/g" deployment.yaml

# Step 3: Build and push the new Docker image
cd src && docker buildx build --push --platform linux/amd64,linux/arm64 -t "olklokk/$APP_NAME:$NEW_VERSION" .

cd .. && kubectl apply -f deployment.yaml
