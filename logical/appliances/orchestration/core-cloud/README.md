# podman orchestration

## create vm

lxc profile create core-cloud
lxc profile edit core-cloud
lxc launch ubuntu:24.04 core-cloud -p default -p core-cloud
lxc exec core-cloud -- bash

## install podman

https://podman.io/docs/installation

sudo apt update && sudo apt install -y podman

## common network for quadlets 
make deploy

## env management
sudo zfs create -o compression=lz4 -o atime=off ssd/appdata/env