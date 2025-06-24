#!/bin/bash

echo "Building and pushing allow-all extension"
./gradlew clean hivemqExtensionZip
scp -r ./build/hivemq-extension/hivemq-allow-all-extension-*.zip ubuntu@192.168.10.2:/var/lib/hivemq/hivemq-allow-all-extension.zip
ssh ubuntu@192.168.10.2 "cd /var/lib/hivemq/extensions && unzip hivemq-allow-all-extension.zip"
