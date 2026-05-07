#!/bin/bash

echo "Building and pushing allow-all extension"
./gradlew clean hivemqExtensionZip
scp -r ./build/hivemq-extension/hivemq-allow-all-extension-*.zip ubuntu@192.168.10.3:/tmp/hivemq-allow-all-extension.zip
ssh ubuntu@192.168.10.3 "cd /tmp && unzip hivemq-allow-all-extension.zip -d /ssd/k3s-temp/hivemq/extensions"
