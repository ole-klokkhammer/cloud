# lxd

## setup
// Reset LXD if it's in a broken state 
sudo snap remove --purge lxd
sudo snap install lxd
sudo usermod -aG lxd $USER
newgrp lxd

// check ethernet device to create bridge on 
ip a

// format lxd disk
sudo lvcreate -L 300G -n lxd-storage ubuntu-vg 

// init lxc
sudo lxd init --preseed < config.yaml

// test
lxc storage list
lxc storage info default
sudo lvs