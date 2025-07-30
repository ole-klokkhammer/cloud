# Storage

* zfs for k3s pool that should be backed up
* lvm k3s volumes with auto provision with local-path
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
Only run volumes that are to be backed up from the database node, master0.

1. Create a lvm that we auto provision k3s volumes to. This will be temporary disks that is not backed up.
  * change default path of local-path provisioner to temp disk. use lvm for this and not zfs?
      * kubectl -n kube-system patch configmap local-path-config --type merge -p '{"data":{"config.json":"{\"nodePathMap\":[{\"node\":\"DEFAULT_PATH_FOR_NON_LISTED_NODES\",\"paths\":[\"/k3s-temp\"]}]}"}}'
2. if we need it on the current node. Create a zfs pool /k3s that is backed up.
    
## big storage
* /mnt/data

## nfs provisioning
https://github.com/kubernetes-sigs/nfs-subdir-external-provisioner?tab=readme-ov-file