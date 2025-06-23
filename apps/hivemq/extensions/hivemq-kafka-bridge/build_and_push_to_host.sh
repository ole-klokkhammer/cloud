#!/bin/bash

echo "Building and pushing allow all extension"
./gradlew clean hivemqExtensionZip
scp -r ./build/hivemq-extension/hivemq-kafka-bridge-*.zip ubuntu@192.168.10.2:/var/lib/hivemq/hivemq-kafka-bridge.zip
ssh ubuntu@192.168.10.2 "cd /var/lib/hivemq && unzip hivemq-kafka-bridge.zip"