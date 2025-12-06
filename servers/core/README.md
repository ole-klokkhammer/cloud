# asrock rack

- upgraded bios
- upgraded firmware
- upgraded intel x55 firmware

## what is
- PXE installation of OS?

## setup

### bios settings 

- ram
  - dram speed 800mhz
  - dram power down enable: disabled
- restore power on ac loss: last state 
- pcie
  - bifurcation on the asrock hyper card
- prevent sleep on aspm
- cmd2t: 2T
- gear down mode: auto # OR ELSE it wont boot
- above 4g decoding: enabled
- sr-iov: disabled
- disable prepare link for power down command: true 

### Ubuntu Server

#### installation

- create three partitions: 
  - efi (1gb by selecting disk as boot)
  - /boot (1GB ext4)
  - / (826.8GB btrfs)
  
- AFTER BOOT ensure both disks are the same:
  - sudo parted /dev/sdX
    - resizepart 3 890GB
    - quit
  - sudo btrfs filesystem resize max / 


#### after boot

- enable cgroup memory reporting if the kernel allows
  - using cgroup v2 with memory
    - sudo nano /etc/default/grub
      - GRUB_CMDLINE_LINUX_DEFAULT="systemd.unified_cgroup_hierarchy=1"
    - sudo update-grub
    - sudo reboot 
- Setup OS disk mirroring
  - sda1 one time backup?
    - 
  - sda2 software mirror (/boot 1GB ext4 with mdadm RAID1):
    - install mdadm:
      - sudo apt install mdadm
    - create RAID1 array using ONLY the backup partition first (sdb2):
      - sudo mdadm --create /dev/md0 \
          --level=1 \
          --raid-devices=2 \
          --metadata=0.90 \
          /dev/sdb2 missing
    - make filesystem on the new array:
      - sudo mkfs.ext4 /dev/md0
    - copy current /boot into the RAID (while still booted from sda2):
      - sudo mount /dev/md0 /mnt/md0
      - sudo rsync -aHAX /boot/ /mnt/md0
      - sudo umount /mnt/md0
    - switch /boot to use the RAID array:
      - sudo mount /dev/md0 /boot
    - add sda2 as the second RAID1 member (now that it’s not in use directly):
      - sudo mdadm --add /dev/md127 /dev/sda2
      - cat /proc/mdstat   # watch it resync
    - fix /etc/fstab to mount /boot from the RAID:
      - get UUID of md0:
        - sudo blkid /dev/md0
      - edit fstab:
        - sudo nano /etc/fstab
        - change /boot line to:
          - UUID=<uuid-of-md0>  /boot  ext4  defaults  0  2
        - remove any /boot entries using /dev/sda2 or /dev/sdb2 directly
    - make mdadm config persistent and update initramfs:
      - sudo mdadm --detail --scan | sudo tee /etc/mdadm/mdadm.conf
      - sudo update-initramfs -u
    - reboot and verify:
      - sudo reboot
      - after reboot:
        - lsblk
        - mount | grep ' /boot'
        - cat /proc/mdstat
        - # /boot should be on /dev/md0 (sda2+sdb2 [raid1])
  - sda3 btrfs mirroring:
    - sudo btrfs device add /dev/sdb3 /
    - sudo btrfs balance start -dconvert=raid1 -mconvert=raid1 /
    - sudo btrfs balance status /
- setup zfs:
  - add ssd pool
  - add hdd pool
  - add db pool
  - install navidrome, aws cli? etc for backup
  - lxd dashboard: https://lxdware.com/
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
- other storage, big and direct mount
  - see readme under storage  

## postgres
## Setup backup 
## k3s