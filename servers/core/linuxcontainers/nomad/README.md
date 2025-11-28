# LXD

## nomad

- lxc profile create nomad
- lxc profile edit nomad
- lxc launch ubuntu:24.04 nomad -p default -p nomad
- lxc exec nomad -- bash 