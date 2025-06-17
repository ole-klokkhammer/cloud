# ceph
https://www.virtualizationhowto.com/2023/08/kubernetes-persistent-volume-setup-with-microk8s-rook-and-ceph/

## setup
https://docs.ceph.com/en/quincy/cephadm/install/#cephadm-install-distros

* sudo apt-get update
* sudo apt-get install cephadm
* sudo cephadm bootstrap --mon-ip 192.168.10.2 --initial-dashboard-user admin --initial-dashboard-password 'initialpasswordissetonfirstlogin'
* sudo cephadm shell -- ceph -s

### add ceph cli
* sudo cephadm add-repo --release quincy
* sudo cephadm install ceph-common 

### dashboard
* sudo ceph mgr services

### add disk

* WIPE DISK: sudo wipefs -a /dev/sd<X> && sudo sgdisk --zap-all /dev/sd<X>
* sudo ceph orch daemon add osd master0:/dev/sd<X> 

### allow for single node single osd setup - no reduncancy
* sudo ceph config set global mon_allow_pool_size_one true
* sudo ceph config set global osd_pool_default_size 1
* sudo ceph config set global mon_warn_on_pool_no_redundancy false 

### pools

rbd for block storage (RADOS Block Device)
cephfs for Ceph Filesystem
rgw for object storage (RADOS Gateway)

### object storage


## commands
* sudo ceph config set global mon_allow_pool_delete true 
* sudo ceph osd pool delete k3s k3s --yes-i-really-really-mean-it
* sudo ceph config set global mon_allow_pool_delete false 

## microceph
https://canonical-microceph.readthedocs-hosted.com/en/latest/how-to/single-node/
poor integration with rook etc

* sudo snap install microceph --classic
* sudo snap refresh --hold microceph
* sudo microceph cluster bootstrap
* sudo microceph status
* sudo microceph add disk /dev/sdX --wipe