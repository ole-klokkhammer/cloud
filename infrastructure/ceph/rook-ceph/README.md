# rook
https://rook.io/docs/rook/latest-release/Getting-Started/intro/
https://docs.rackspacecloud.com/storage-ceph-rook-external/#validate-the-connection
https://rook.io/docs/rook/latest-release/CRDs/Cluster/external-cluster/provider-export/
https://github.com/rook/rook/blob/release-1.17/deploy/examples/external

## setup

### setup mds (metadata) service for multi-attach kubernetes volumes
* sudo ceph orch host label add master0 mds
* sudo ceph orch apply mds myfs label:mds

### setup pools
Create block storage and shared storage: rbd + cephfs

* sudo ceph osd pool create k3s-rbd 32
* sudo rbd pool init k3s-rbd
* sudo ceph osd pool create k3s-cephfs-data 32
* sudo ceph osd pool create k3s-cephfs-metadata 32 
* sudo ceph fs new k3s-cephfs k3s-cephfs-data k3s-cephfs-metadata
* sudo ceph orch apply rgw default --placement="1 master0"

### install 
* kubectl ./deploy/operator
* kubectl ./deploy/cluster
* kubectl ./deploy/cluster


### import cluster data
* cd /tmp
* wget https://raw.githubusercontent.com/rook/rook/release-1.17/deploy/examples/create-external-cluster-resources.py 
* sudo python3 create-external-cluster-resources.py \
  --rbd-data-pool-name k3s-rbd \
  --cephfs-filesystem-name k3s-multi-attach \
  --cephfs-metadata-pool-name k3s-cephfs-metadata \
  --rgw-endpoint '192.168.10.2:80' \
  --namespace rook-ceph \
  --format bash
* set export vars in ./import-external-cluster.sh
* change script to set persistentVolumeReclaimPolicy: Retain
this way we can create volumes with kubernetes, then retain them independently
* ./import-external-cluster.sh 
 

## test storageclasses
https://github.com/rook/rook/tree/release-1.17/deploy/examples/csi
https://github.com/ceph/ceph-csi/blob/devel/docs/static-pvc.md

## static volumes
https://github.com/ceph/ceph-csi/blob/devel/docs/static-pvc.md

## defaults
* ceph auth get client.csi-cephfs-provisioner 
[client.csi-cephfs-provisioner]
	key = AQDGRFFo75D6MRAAf2ogcCP604/jKT3iPPPM8g==
	caps mds = "allow *"
	caps mgr = "allow rw"
	caps mon = "allow r, allow command 'osd blocklist'"
	caps osd = "allow rw tag cephfs metadata=*"
* ceph auth get client.csi-rbd-provisioner
[client.csi-rbd-provisioner]
	key = AQDGRFFohZukMRAAvV077gZb4D5EvnQOvsuz2w==
	caps mgr = "allow rw"
	caps mon = "profile rbd, allow command 'osd blocklist'"
	caps osd = "profile rbd"

## allow all
* ceph auth caps client.csi-cephfs-provisioner mon 'allow *' mgr 'allow *' osd 'allow *' mds 'allow *'
* ceph auth caps client.csi-rbd-provisioner mon 'allow *' mgr 'allow *' osd 'allow *' mds 'allow *'
