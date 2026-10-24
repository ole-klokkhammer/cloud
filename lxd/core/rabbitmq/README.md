# LXD

## rabbitmq
https://www.rabbitmq.com/docs/install-debian#installation-methods

- lxc profile create rabbitmq
- lxc profile edit rabbitmq
- lxc launch ubuntu:24.04 rabbitmq -p default -p rabbitmq
- lxc exec rabbitmq -- bash 


## setup

https://www.rabbitmq.com/docs/install-debian