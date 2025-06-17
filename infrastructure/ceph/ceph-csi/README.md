# ceph
https://github.com/ceph/ceph-csi
https://github.com/ceph/ceph-csi/blob/devel/deploy/ceph-conf.yaml

## rook
https://gist.github.com/alexcpn/79d72678f28c1bed76ba28d49228a638
https://docs.rackspacecloud.com/storage-ceph-rook-external/#prepare-pools-on-external-cluster

* ssh to server
* sudo ceph orch host label add genestack-ceph1 mds
* sudo ceph orch apply mds myfs label:mds
* 
* 
* sudo apt install python3-rados python3-rbd
* wget https://raw.githubusercontent.com/rook/rook/release-1.17/deploy/examples/create-external-cluster-resources.py
* python3 create-external-cluster-resources.py --rbd-data-pool-name general --cephfs-filesystem-name general-multi-attach --namespace rook-ceph-external --format bash

## ceph csi 
* kubectl create secret generic ceph-secret \
  --from-literal=key=AQBWV0dosRv9AhAA0CcxZoAxKUZ+qHVY7cdjEA== 
* kubectl apply -f configmap.yaml
* kubectl apply -f csi-provisioner-rbac.yaml
* kubectl apply -f csi-nodeplugin-rbac.yaml
* kubectl apply -f csi-rbdplugin-provisioner.yaml
* kubectl apply -f csi-rbdplugin.yaml
* kubectl apply -f service.yaml
* kubectl apply -f storageclass.yaml
* kubectl apply -f test.yaml