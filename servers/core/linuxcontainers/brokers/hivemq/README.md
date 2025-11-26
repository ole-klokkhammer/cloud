# LXD

## hivemq

- lxc profile create hivemq
- lxc profile edit hivemq
- lxc launch ubuntu:24.04 hivemq -p default -p hivemq
- lxc exec hivemq -- bash 
  - sudo apt update
 