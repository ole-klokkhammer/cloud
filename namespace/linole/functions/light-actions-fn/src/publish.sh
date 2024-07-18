#!/bin/bash


docker buildx build --push --platform linux/amd64,linux/arm64 -t olklokk/lightscene-mqtt:latest .

