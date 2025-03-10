#!/bin/bash

docker build -t lightscene-mqtt . && docker run --rm -it --name lightscene-mqtt lightscene-mqtt
