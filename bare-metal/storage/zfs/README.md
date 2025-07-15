# zfs

## setup

### 1. Install ZFS

sudo apt update
sudo apt install zfsutils-linux

### 2. Load ZFS Kernel Module

sudo modprobe zfs

### 3. Create a ZFS Pool

* sudo zpool create k3s /dev/nvme0n1p1
* sudo zpool create k3s-temp /dev/nvme0n1p2

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

### 8. set script permissions
for backup
* zfs allow ubuntu snapshot k3s

## restoring volumes 

* aws s3 cp --profile k3s-volume-backup s3://k3s-volumes/k3s/homeassistant-data/snapshot-1752566019.zfs /tmp --endpoint-url https://j8t7.ldn203.idrivee2-94.com
* sudo zfs receive k3s/homeassistant-data < /tmp/snapshot-1752566019.zfs