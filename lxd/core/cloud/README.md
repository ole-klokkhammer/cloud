# podman orchestration

## create vm

lxc profile create cloud
lxc profile edit cloud
lxc launch ubuntu:26.04 cloud -p default -p cloud
lxc exec cloud -- bash
