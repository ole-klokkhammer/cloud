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
- backup:
  - sudo dd if=/dev/sda1 of=/dev/sdb1 bs=4M status=progress
  - sudo dd if=/dev/sda2 of=/dev/sdb2 bs=4M status=progress
  - sudo mount /dev/sdb3 /mnt/backup_btrfs
    - sudo btrfs subvolume snapshot -r / /snap-root
    - sudo btrfs send /snap-root | sudo btrfs receive /mnt/backup_btrfs
    - sudo btrfs subvolume snapshot /mnt/backup_btrfs/snap-root /mnt/backup_btrfs/@
    - Set @ as the default subvolume on the backup disk:
      - sudo btrfs subvolume set-default /mnt/backup_btrfs/@
    - Now when /dev/sdb3 is mounted without subvol options, it will mount @ as /.
    - optionally delete
      - sudo btrfs subvolume delete /snap-root
      - sudo btrfs subvolume delete /mnt/backup_btrfs/snap-root



#### after boot

- enable cgroup memory reporting if the kernel allows
  - using cgroup v2 with memory
    - sudo nano /etc/default/grub
      - GRUB_CMDLINE_LINUX_DEFAULT="systemd.unified_cgroup_hierarchy=1"
    - sudo update-grub
    - sudo reboot 
- Setup OS disk backup
  - duplicate the efi and boot, and create a mirror of root on a seperate disk
    - sudo parted /dev/sdb
      - mklabel gpt
      - mkpart ESP fat32 1MiB 1025MiB
      - set 1 boot off
      - set 1 esp on
      - mkpart boot ext4 1025MiB 2049MiB
      - mkpart root btrfs 2049MiB 204801MiB
      - quit
    - sudo mkfs.fat -F32 /dev/sdb1
    - sudo mkfs.ext4 /dev/sdb2
    - sudo mkfs.btrfs /dev/sdb3
    - Ensure GRUB on the backup points to the backup root
      - # Mount backup root with subvol=@
      - sudo mount -o subvol=@ /dev/sdb3 /mnt/backup_root
      - sudo mount /dev/sdb1 /mnt/backup_root/boot/efi
      - sudo mount /dev/sdb2 /mnt/backup_root/boot
      - 
      - sudo mount --bind /dev  /mnt/backup_root/dev
      - sudo mount --bind /proc /mnt/backup_root/proc
      - sudo mount --bind /sys  /mnt/backup_root/sys

      - sudo chroot /mnt/backup_root /bin/bash

        # inside chroot:
      - grub-install /dev/sdb
      - update-grub
      - exit
  - backup:
    - sudo dd if=/dev/sda1 of=/dev/sdb1 bs=4M status=progress
    - sudo dd if=/dev/sda2 of=/dev/sdb2 bs=4M status=progress
    - sudo mount /dev/sdb3 /mnt/backup_btrfs
      - sudo btrfs subvolume snapshot -r / /snap-root
      - sudo btrfs send /snap-root | sudo btrfs receive /mnt/backup_btrfs
      - sudo btrfs subvolume snapshot /mnt/backup_btrfs/snap-root /mnt/backup_btrfs/@
      - Set @ as the default subvolume on the backup disk:
        - sudo btrfs subvolume set-default /mnt/backup_btrfs/@
      - Now when /dev/sdb3 is mounted without subvol options, it will mount @ as /.
      - optionally delete
        - sudo btrfs subvolume delete /snap-root
        - sudo btrfs subvolume delete /mnt/backup_btrfs/snap-root
  - NOW IN CASE OF DISK FAILURE:
    Keep set 1 boot off on sdb1 normally.
    When sda dies, go into BIOS, flip sdb1 to boot on using parted from a rescue stick, or just pick its EFI entry manually in the firmware menu.
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