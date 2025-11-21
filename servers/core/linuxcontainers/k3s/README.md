# lxd 
- lxc profile create k3s
- lxc profile edit k3s
- lxc launch ubuntu:24.04 k3s -p default -p k3s
- lxc exec k3s -- bash


## notes on bind mounts
- zfs: bind mounts must be the same as on the host
- use shift: "true" for easier permissions management

## mitigations to prevent running in privelieged mode
- prevent writing kernel logs, otherwise we need privelieged mode
  - sudo ln -s /dev/null /dev/kmsg
- sudo hostnamectl set-hostname master0
- ensure ip is the same as restored config