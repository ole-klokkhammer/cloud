#!/bin/bash

echo "Building and pushing allow-all extension"
./gradlew clean hivemqExtensionZip
scp -r ./build/hivemq-extension/hivemq-allow-all-extension-*.zip ubuntu@192.168.10.2:/tmp/hivemq-allow-all-extension.zip
ssh ubuntu@192.168.10.2 "cd /tmp && unzip hivemq-allow-all-extension.zip -d /k3s-temp/hivemq/extensions"
