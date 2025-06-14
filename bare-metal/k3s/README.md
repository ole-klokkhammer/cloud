# master on x86_64 ubuntu server
* https://docs.k3s.io/installation/requirements?os=debian 
* https://metalcoder.dev/making-k3s-stop-hoarding-disk-space/

``## disable firewall
* ufw disable

## Define server token at ~/.k3s/k3s-server-token
* K3S_TOKEN=<find-in-keystore>
* K3S_TOKEN_FILE=~/.k3s/k3s-server-token

## Add shutdown script (optional)
* alias killK3s="/usr/local/bin/k3s-killall.sh"


## Install 
`curl -sfL https://get.k3s.io | K3S_TOKEN_FILE=~/.k3s/k3s-server-token INSTALL_K3S_EXEC="\
server \
'--disable' \
'traefik' \
'--disable' \
'servicelb' \
'--write-kubeconfig-mode' \
'644' \
--etcd-s3 \
--etcd-s3-config-secret='etcd-s3-config' \
--cluster-init
"  sh -
`

## on clients 
* copy certificates: sudo cat /etc/rancher/k3s/k3s.yaml > ~/.kube/config
* replace ip with actual

## system services

1. setup metalb loadbalancer (https://metallb.universe.tf/installation/)
   * cd ./metalLB + follow readme 

2. add nginx ingress controller
    * cd ./nginx-ingress + follow readme
 
3. setup cert-manager
   * cd ./cert-manager + follow readme

4. setup dashboard
   * cd ./kubernetes-dashboard + follow readme
 
5. setup nvidia
   * cd ./nvidia + follow readme
 
6. setup longhorn
   * cd ./longhorn + follow readme

## external database
### prepare database
* sudo -u postgres psql -c "CREATE DATABASE k3s;"
* sudo -u postgres psql -c "CREATE USER k3s WITH PASSWORD <input from keystore>;"
* sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE k3s TO k3s;"

## clients
* copy /etc/rancher/k3s/k3s.yaml from the master node to local ~/.kube/config
* replace the master node ip with the actual ip


## etcd restore
 reinstall k3s, stop the service, then:
 sudo k3s server \
  --cluster-init \
  --cluster-reset \
  --etcd-s3 \
  --cluster-reset-restore-path=etcd-snapshot-master0-1749297605 \
  --etcd-s3-bucket=k3s \
  --etcd-s3-access-key=  \
  --etcd-s3-secret-key=  \
  --etcd-s3-endpoint=j8t7.ldn203.idrivee2-94.com \
  --etcd-s3-region=London-2

## force delete terminating namespaces


* (
NAMESPACE=your-rogue-namespace
kubectl proxy &
kubectl get namespace $NAMESPACE -o json |jq '.spec = {"finalizers":[]}' >temp.json
curl -k -H "Content-Type: application/json" -X PUT --data-binary @temp.json 127.0.0.1:8001/api/v1/namespaces/$NAMESPACE/finalize
)