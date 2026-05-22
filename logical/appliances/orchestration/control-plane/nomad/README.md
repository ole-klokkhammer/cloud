# control-plane 

## storage
sudo zfs create -o compression=lz4 -o atime=off ssd/appdata/control-plane
sudo zfs set logbias=latency ssd/appdata/control-plane

## control-plane 

- lxc profile create control-plane 
- lxc profile edit control-plane 
- lxc launch ubuntu:24.04 control-plane  -p default -p control-plane 
- lxc exec control-plane  -- bash
 