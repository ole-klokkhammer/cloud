# LXD

## hivemq
https://github.com/hivemq/hivemq-community-edition/wiki/Configuration

- lxc profile create hivemq
- lxc profile edit hivemq
- lxc launch ubuntu:24.04 hivemq -p default -p hivemq
- lxc exec hivemq -- bash 
  - sudo apt update
    sudo apt install openjdk-17-jre-headless
    cd /tmp
    wget https://github.com/hivemq/hivemq-community-edition/releases/download/2025.5/hivemq-ce-2025.5.zip
    unzip hivemq-ce-2025.5.zip
    mv ./hivemq-ce-2025.5 /opt/hivemq/2025.5
    cd hivemq-ce-2025.5
    ./bin/run.sh