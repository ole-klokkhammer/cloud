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
* sudo ceph fs new k3s-multi-attach k3s-cephfs-data k3s-cephfs-metadata


### create vars
* cd /tmp
* wget https://raw.githubusercontent.com/rook/rook/release-1.17/deploy/examples/create-external-cluster-resources.py 
* sudo python3 create-external-cluster-resources.py \
  --rbd-data-pool-name k3s-rbd \
  --cephfs-filesystem-name k3s-multi-attach \
  --cephfs-metadata-pool-name k3s-cephfs-metadata \
  --namespace rook-ceph-external \
  --format bash

### apply helm charts
* https://github.com/rook/rook
* cd deploy/examples/charts/rook-ceph-cluster
* helm repo add rook-release https://charts.rook.io/release
* helm repo update
* helm install \
  --create-namespace \
  --namespace rook-ceph-external \
  rook-ceph  \
  rook-release/rook-ceph \
  -f values-operator.yaml
* helm install \
  --create-namespace  \
  --namespace rook-ceph-external \
  rook-ceph-cluster \
  --set operatorNamespace=rook-ceph-external \
  rook-release/rook-ceph-cluster \
  -f values-cluster.yaml

### import vars to cluster
* cd /tmp
* wget https://raw.githubusercontent.com/rook/rook/release-1.17/deploy/examples/import-external-cluster.sh
* set env vars from external cluster
* ./import-external-cluster.sh
* kubectl -n rook-ceph  get CephCluster
* kubectl -n rook-ceph get sc


## test storageclasses
https://github.com/rook/rook/tree/release-1.17/deploy/examples/csi