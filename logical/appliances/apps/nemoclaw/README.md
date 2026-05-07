# nemoclaw
https://www.nvidia.com/en-us/ai/nemoclaw/
https://nemoclawai.io/

## setup

## Disk
sudo zfs create -o compression=lz4 -o atime=off -o xattr=sa -o acltype=posixacl -o recordsize=1M ssd/appdata/nemoclaw

### lxc
- lxc profile create nemoclaw
- lxc profile edit nemoclaw
- lxc launch ubuntu:24.04 nemoclaw -p default -p nemoclaw
- lxc exec nemoclaw -- bash 


### dependencies
sudo apt update
