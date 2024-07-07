# raspernetes
https://github.com/raspbernetes

# 
* https://github.com/toboshii/home-cluster

# SETTING UP
https://kauri.io/#install-and-configure-a-kubernetes-cluster-with-k3s-to-self-host-applications/418b3bc1e0544fbc955a4bbba6fff8a9/a
https://thenewstack.io/tutorial-install-a-highly-available-k3s-cluster-at-the-edge/
https://rpi4cluster.com/k3s/k3s-kube-setting/#done
We will install k3s with nginx and metallb. Using m.2 ssd on rpis as storage

# COMPUTE MODULE 4 SETUP

## basic setup
* Go to /boot/firmware/cmdline.txt and add cgroup_enable=cpuset cgroup_memory=1 cgroup_enable=memory
* sudo apt install linux-modules-extra-raspi
* sudo apt-get install open-iscsi
* Set hostnames
* sudo apt update
  sudo apt upgrade -y
  sudo apt install iptables -y
  sudo iptables -F
  sudo update-alternatives --set iptables /usr/sbin/iptables-legacy
  sudo update-alternatives --set ip6tables /usr/sbin/ip6tables-legacy 

## Mount disk
sudo fdisk -l
sudo fdisk /dev/nvme0n1
sudo mkfs.ext4 /dev/nvme0n1
sudo mkdir /mnt/disk1/k3s
sudo nano /etc/fstab
-- UUID="..." /mnt/disk1 ext4 nosuid,nodev,nofail,x-gvfs-show 0 0


## Define server token at ~/.k3s/k3s-server-token
K3S_TOKEN=<lastpass>
K3S_TOKEN_FILE=~/.k3s/k3s-server-token

## Prevent writing too much logs
* cat /etc/systemd/journald.conf
* use storage none for journald
* sudo systemctl restart systemd-journald
- or install log2ram https://github.com/azlux/log2ram

## Add shutdown script
* alias killK3s="/usr/local/bin/k3s-killall.sh"


# install

## on master:
`curl -sfL https://get.k3s.io | K3S_TOKEN_FILE=~/.k3s/k3s-server-token INSTALL_K3S_EXEC="\
server \
'--disable' \
'traefik' \
'--disable' \
'servicelb' \
'--write-kubeconfig-mode' \
'644' \
'--data-dir' \
'/mnt/disk1/k3s' \
'--etcd-s3' \
'--etcd-s3-endpoint' \
'gateway.eu1.storjshare.io' \
'--etcd-s3-access-key' \
'jvlm7ugdddnuggeyt3ssry3tdbfa' \
'--etcd-s3-secret-key' \
'j3xuneoh5n62g3dsvrxtciywcunlanmfzmgtg6baibst5kk74tiig' \
'--etcd-s3-region' \
'eu-north-1' \
'--etcd-s3-bucket' \
'linole-k3s-etcd' \
"  sh -
` 

### on joining masters:
`curl -sfL https://get.k3s.io | K3S_TOKEN_FILE=~/.k3s/k3s-server-token K3S_URL=https://192.168.10.2:6443 INSTALL_K3S_EXEC="\
server \
'--disable' \
'traefik' \
'--disable' \
'servicelb' \
'--write-kubeconfig-mode' \
'644' \
'--data-dir' \
'/mnt/disk1/k3s' \
'--etcd-s3' \
'--etcd-s3-endpoint' \
's3.eu-north-1.amazonaws.com' \
'--etcd-s3-access-key' \
'jvlm7ugdddnuggeyt3ssry3tdbfa' \
'--etcd-s3-secret-key' \
'j3xuneoh5n62g3dsvrxtciywcunlanmfzmgtg6baibst5kk74tiig' \
'--etcd-s3-region' \
'eu-north-1' \
'--etcd-s3-bucket' \
'linole-k3s-etcd' \
"  sh -
`

### if joining after some time:
* copy certificates etc:
* 

### restore from s3
* run on all masters:
`
K3S_TOKEN_FILE=~/.k3s/k3s-server-token
sudo k3s server \ 
'--cluster-init' \
'--cluster-reset' \
'--data-dir' \
'/mnt/disk1/k3s' \
'--etcd-s3' \
'--cluster-reset-restore-path=etcd-snapshot-node1-1653652800' \
'--etcd-s3-endpoint' \
's3.eu-north-1.amazonaws.com' \
'--etcd-s3-access-key' \
'jvlm7ugdddnuggeyt3ssry3tdbfa' \
'--etcd-s3-secret-key' \
'j3xuneoh5n62g3dsvrxtciywcunlanmfzmgtg6baibst5kk74tiig' \
'--etcd-s3-region' \
'eu-north-1' \
'--etcd-s3-bucket' \
'linole-k3s-etcd' 
`
 

## agents
* add data dir for external storage?
`curl -sfL https://get.k3s.io | K3S_TOKEN_FILE=~/.k3s/k3s-server-token K3S_URL=https://192.168.10.2:6443 INSTALL_K3S_EXEC="\
'agent' \
'--data-dir' \
'/mnt/disk1/k3s' \
"  sh -
  `
* update k3s.yaml for kubectl: /etc/rancher/k3s$ cat k3s.yaml

# label nodes
* kubectl label nodes node0 node-role.kubernetes.io/worker=worker
* kubectl label nodes node1 node-role.kubernetes.io/worker=worker
* kubectl label nodes node2 node-role.kubernetes.io/worker=worker
* kubectl taint nodes master0 node-role.kubernetes.io/master=:NoSchedule

## BACKUP
* `
k3s etcd-snapshot \
'--data-dir' \
'/mnt/disk1/k3s' \
'--s3' \
'--s3-endpoint' \
's3.eu-north-1.amazonaws.com' \
'--s3-access-key' \
'jvlm7ugdddnuggeyt3ssry3tdbfa' \
'--s3-secret-key' \
'j3xuneoh5n62g3dsvrxtciywcunlanmfzmgtg6baibst5kk74tiig' \
'--s3-region' \
'eu-north-1' \
'--s3-bucket' \
'linole-k3s-etcd'
  `

## PFSENSE
https://www.danmanners.com/posts/2019-02-pfsense-bgp-kubernetes/
* see metalb config
* install openbgp on pfsense
* virtual ip range
* assign ips for each node


## Commands

* kubectl api-resources --verbs=list --namespaced -o name | xargs -n 1 kubectl get --show-kind --ignore-not-found -n <ns>
* kubectl get svc --all-namespaces
* kubectl get all -n <namespace>
* kubectl get deployments -n minio | tail +2 | awk '{ cmd=sprintf("kubectl rollout restart deployment -n %s %s", $1, $2) ; system(cmd) }'
* sudo k3s kubectl -n kubernetes-dashboard describe secret admin-user-token | grep '^token'
* kubectl get -n kube-system cm/local-path-config -o yaml