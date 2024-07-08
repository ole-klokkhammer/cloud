#!/bin/bash


docker buildx build --push --platform linux/amd64,linux/arm64 -t olklokk/scheduler:1.0.0 .

