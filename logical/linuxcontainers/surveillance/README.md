# Surveillance

## setup

### lxc

lxc profile create surveillance 
lxc profile edit surveillance 
lxc launch ubuntu:24.04 surveillance -p default -p surveillance
lxc exec surveillance -- bash

#### install podman

sudo apt update && sudo apt install -y podman systemd-container gettext-base
systemctl enable --now podman-auto-update.timer

