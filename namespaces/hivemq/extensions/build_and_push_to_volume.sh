#!/bin/bash

echo "Building and pushing authorization extension to HiveMQ volume"
cd hivemq-allow-all-extension
./gradlew hivemqExtensionZip
scp -r ./build/hivemq-extension/hivemq-allow-all-extension-*.zip ubuntu@192.168.10.2:/var/lib/hivemq
ssh ubuntu@192.168.10.2 "unzip /var/lib/hivemq/hivemq-extension/hivemq-allow-all-extension-*.zip"

echo "Building and pushing kafka extension"
cd hivemq-kafka-bridge
./gradlew hivemqExtensionZip
scp -r ./build/hivemq-extension/hivemq-kafka-bridge-*.zip ubuntu@192.168.10.2:/var/lib/hivemq
ssh ubuntu@192.168.10.2 "unzip /var/lib/hivemq/hivemq-extension/hivemq-kafka-bridge-*.zip"