# lxd

## setup
// Reset LXD if it's in a broken state 
sudo snap remove --purge lxd
sudo snap install lxd
sudo usermod -aG lxd $USER
newgrp lxd

// check ethernet device to create bridge on 
ip a

// check lvm pool
sudo vgs
sudo lvs
sudo lvcreate -L 400G -n lxd-storage ubuntu-vg
sudo mkfs.ext4 /dev/ubuntu-vg/lxd-storage
sudo mkdir -p /mnt/lxd-storage
sudo mount /dev/ubuntu-vg/lxd-storage /mnt/lxd-storage

// persistent mount
sudo blkid /dev/ubuntu-vg/lxd-storage
echo "UUID=b991fe54-d081-4089-8a5a-5e2ab2675df9 /mnt/lxd-storage ext4 defaults 0 2" | sudo tee -a /etc/fstab 
sudo mount -a

// extend ubuntu-lv to use the rest
sudo lvextend -l +100%FREE /dev/ubuntu-vg/ubuntu-lv

// init lxc
sudo lxd init --preseed < config.yaml

// test
lxc storage list
lxc storage info default
sudo lvs