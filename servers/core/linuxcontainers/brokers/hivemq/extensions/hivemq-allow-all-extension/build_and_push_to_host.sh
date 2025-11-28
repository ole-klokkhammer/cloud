#!/bin/bash

echo "Building and pushing allow-all extension"
./gradlew clean hivemqExtensionZip
scp -r ./build/hivemq-extension/hivemq-allow-all-extension-*.zip ubuntu@core.home.lan:/tmp/hivemq-allow-all-extension.zip
ssh ubuntu@core.home.lan "cd /tmp && unzip hivemq-allow-all-extension.zip -d /ssd/appdata/hivemq/extensions"
