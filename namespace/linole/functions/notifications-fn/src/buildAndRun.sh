#!/bin/bash

docker build -t notifications . && docker run --rm -it --name notifications notifications
