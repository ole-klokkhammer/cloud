# frigate

## setup

### disk

sudo zfs create -o compression=lz4 -o atime=off -o xattr=sa -o acltype=posixacl -o recordsize=1M ssd/appdata/frigate

### lxc

lxc profile create frigate
lxc profile edit frigate
lxc launch ubuntu:24.04 frigate -p default -p frigate
lxc exec frigate -- bash

#### install podman

https://podman.io/docs/installation

sudo apt update && sudo apt install -y podman systemd-container 

enable auto update
systemctl enable --now podman-auto-update.timer
systemctl list-timers | grep podman-auto-update

#### start frigate

