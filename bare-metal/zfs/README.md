# zfs

## setup

### 1. Install ZFS

sudo apt update
sudo apt install zfsutils-linux

### 2. Load ZFS Kernel Module

sudo modprobe zfs

### 3. Create a ZFS Pool

sudo zpool create mypool /dev/sdX

### 4. Create a ZFS Filesystem
sudo zfs create mypool/mydataset

### 5. Mount and Use

ZFS filesystems are mounted automatically under `/mypool/mydataset` by default.

### 6. Check Status
 
sudo zpool status
sudo zfs list 

### 7. Enable at Boot

ZFS services are enabled by default on most distributions.
sudo systemctl enable zfs-import-cache
sudo systemctl enable zfs-mount

