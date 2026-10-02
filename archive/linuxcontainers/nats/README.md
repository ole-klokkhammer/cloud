# LXD

## setup

lxc profile create nats
lxc profile edit nats
lxc launch ubuntu:24.04 nats -p default -p nats
lxc exec nats -- bash 

