# unifi os


## setup

### Disk
sudo zfs create -V 20G \
  -o volblocksize=16K \
  -o compression=lz4 \
  ssd/vm/unifi

### lxc 
lxc profile create unifi-vm
lxc profile edit unifi-vm
lxc launch ubuntu:24.04 unifi --vm -p default -p unifi-vm

// setup the disk if not already done
lxc exec unifi -- sudo --login --user ubuntu
lsblk
sudo mkfs.ext4 /dev/sdb
sudo mkdir -p /home
sudo mount /dev/sdb /home
sudo mkdir -p /home/uosserver

sudo blkid /dev/sdb
sudo nano /etc/fstab
UUID=<uuid-from-blkid> /home ext4 defaults 0 2

sudo umount /home
sudo mount -a
df -h /home

### installation
lxc exec unifi -- sudo --login --user ubuntu

#### prerequisits
sudo apt update
sudo apt install -y podman uidmap slirp4netns fuse-overlayfs curl ca-certificates

#### install
https://www.ui.com/download

// ensure permissions
sudo ls -ld /home /home/uosserver
sudo id uosserver
sudo chown -R uosserver:uosserver /home/uosserver
sudo chmod 750 /home/uosserver

// download and install
cd /tmp
curl -L -o uosserver-5.0.8 https://fw-download.ubnt.com/data/unifi-os-server/c2e4-linux-x64-5.0.8-bcb62759-753a-4be2-8546-a6e0de63e59a.8-x64
chmod +x ./uosserver-5.0.8
sudo ./uosserver-5.0.8


### access
https://192.168.10.214:11443/setup/device-name