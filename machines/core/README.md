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
- later duplicate the efi and boot, and create a mirror of root

#### after boot

- setup zfs:
  - add ssd pool
  - add hdd pool
  - add db pool
- install lxd:
  - sudo apt install apparmor apparmor-utils
  - sudo aa-status
  - sudo snap install lxd
  - sudo zfs create ssd/lxd
  - sudo lxd init
  - lxc storage create zpool zfs source=ssd/lxd
  - lxc profile device set default root pool zpool
  - create seperate pool for config storage: ssd/lxd-configs
- gpu deps
  -  nvidia
  - amd
- aws cli
  - setup aws cli and add profiles
- other storage
  - see readme under storage  

## postgres
## Setup backup 
## k3s