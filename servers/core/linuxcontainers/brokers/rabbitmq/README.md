# LXD

## rabbitmq

- lxc profile create rabbitmq
- lxc profile edit rabbitmq
- lxc launch ubuntu:24.04 rabbitmq -p default -p rabbitmq
- lxc exec rabbitmq -- bash 
  - sudo apt update
    sudo apt install rabbitmq-server
    sudo systemctl enable rabbitmq-server
    sudo systemctl start rabbitmq-server