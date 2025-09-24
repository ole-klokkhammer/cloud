# master on x86_64 ubuntu server
* https://docs.k3s.io/installation/requirements?os=debian 
* https://metalcoder.dev/making-k3s-stop-hoarding-disk-space/

## Prerequisits
``## disable firewall
* ufw disable 
* swap off: comment out swap in /etc/fstab

### Define server token at ~/.k3s/k3s-server-token
* K3S_TOKEN=<find-in-keystore>
* K3S_TOKEN_FILE=~/.k3s/k3s-server-token

### Add shutdown script (optional)
* alias killK3s="/usr/local/bin/k3s-killall.sh"

### disable ipv6 on os level??
* sudo nano /etc/sysctl.d/99-disable-ipv6.conf
   net.ipv6.conf.all.disable_ipv6 = 1
   net.ipv6.conf.default.disable_ipv6 = 1
* sudo sysctl --system

### set ulimit
ulimit -n 65536
* sudo nano /etc/security/limits.conf and add:
  * soft nofile 65536
  * hard nofile 65536 

* echo "fs.inotify.max_user_instances=1024" | sudo tee -a /etc/sysctl.conf
* sudo sysctl -p

### prevent service restart on apt-get install
sudo systemctl edit k3s.service
[Service]
Restart=no
sudo systemctl daemon-reload

### ensure postgres is setup

## Install 
`curl -sfL https://get.k3s.io | K3S_TOKEN_FILE=~/.k3s/k3s-server-token INSTALL_K3S_EXEC="\
server \
'--disable' \
'traefik' \
'--disable' \
'servicelb' \
'--write-kubeconfig-mode' \
'644' \
'--datastore-endpoint' \
'postgres://k3s:<pass>@192.168.10.2:5432/k3s?sslmode=disable' \
--cluster-init
"  sh -
`

### set ulimit
* sudo systemctl edit k3s.service
* [Service]
LimitNOFILE=65536
* sudo systemctl daemon-reload
* sudo systemctl restart k3s.service

## on clients 
* copy certificates: sudo cat /etc/rancher/k3s/k3s.yaml > ~/.kube/config
* replace ip with actual


## Commands
### force delete terminating namespaces


* (
NAMESPACE=your-rogue-namespace
kubectl proxy &
kubectl get namespace $NAMESPACE -o json |jq '.spec = {"finalizers":[]}' >temp.json
curl -k -H "Content-Type: application/json" -X PUT --data-binary @temp.json 127.0.0.1:8001/api/v1/namespaces/$NAMESPACE/finalize
)