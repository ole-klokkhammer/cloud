# Storage

* zfs for k3s pool
* temp storage for k3s volumes
* postgres at /mnt/databases/postgres
* etcd at /mnt/databases/etcd

## NOTICE
mount disks with UUID for reliability

## databases
* sudo blkid
* sudo mkdir -p /mnt/databases
* sudo mount UUID=<your-uuid-here> /mnt/databases
* sudo nano /etc/fstab
* UUID=<your-uuid-here>  /mnt/databases  ext4  defaults  0  2
* sudo mount -a

## k3s volumes
* split 1 TB disk in two: temp and k3s backed up vols
* 

## big storage
* /mnt/data