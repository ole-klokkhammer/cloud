#!/bin/bash

zip -r job.zip job.py
curl -X POST -H "Content-Type: multipart/form-data" \
    -F "jarfile=@job.zip" \
    http://192.168.10.214:8081/jars/upload