# asrock rack

- upgraded bios
- upgraded firmware
- upgraded intel x55 firmware

## what is
- PXE installation of OS?

## setup

### bios settings 

- downclocked to 1600mhz 
- bifurcation on the asrock hyper card
- prevent sleep on aspm


### Ubuntu Server

#### installation

- create three partitions: 
  - efi (by selecting disk as boot)
  - /boot (1GB ext4)
  - / (200GB btrfs)

#### after boot

- enable cgroup memory reporting if the kernel allows
  - using cgroup v2 with memory
    - sudo nano /etc/default/grub
      - GRUB_CMDLINE_LINUX_DEFAULT="systemd.unified_cgroup_hierarchy=1"
    - sudo update-grub
    - sudo reboot 
- duplicate the efi and boot, and create a mirror of root on a seperate disk
- setup zfs:
  - add ssd pool
  - add hdd pool
  - add db pool
- LAN BRIDGE: create a real bridge for networking on the host, use this for exposing the services on local ips issued by the main dhcp
  - see netplan
  - br0 -> eth0
  - br1 -> eth1
- install lxd:
  - sudo apt install apparmor apparmor-utils
  - sudo aa-status
  - sudo snap install lxd
  - sudo zfs create ssd/lxd
  - sudo lxd init
  - lxc storage create zpool zfs source=ssd/lxd
  - lxc profile device set default root pool zpool
  - create seperate pool for config storage: ssd/lxd-configs 
- install gpu deps
  - nvidia
- install k3s
  - 
- aws cli
  - setup aws cli and add profiles
- other storage, big and direct mount
  - see readme under storage  

## postgres
## Setup backup 
## k3s