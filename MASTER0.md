# master on x86_64 ubuntu server
* https://docs.k3s.io/installation/requirements?os=debian 

## disable firewall
* ufw disable

## Define server token at ~/.k3s/k3s-server-token
* K3S_TOKEN=<find-in-keystore>
* K3S_TOKEN_FILE=~/.k3s/k3s-server-token

## Add shutdown script (optional)
* alias killK3s="/usr/local/bin/k3s-killall.sh"

## prepare database
* sudo -u postgres psql -c "CREATE DATABASE k3s;"
* sudo -u postgres psql -c "CREATE USER k3s WITH PASSWORD <input from keystore>;"
* sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE k3s TO k3s;"

## Install 
`curl -sfL https://get.k3s.io | K3S_TOKEN_FILE=~/.k3s/k3s-server-token INSTALL_K3S_EXEC="\
server \
'--disable' \
'traefik' \
'--disable' \
'servicelb' \
'--write-kubeconfig-mode' \
'644' \
--datastore-endpoint \
'postgres://username:password@hostname:port/k3s'
"  sh -
`

## on clients 
* copy certificates: sudo cat /etc/rancher/k3s/k3s.yaml > ~/.kube/config

## system services

1. setup metalb loadbalancer (https://metallb.universe.tf/installation/)
   * cd ./metalLB + follow readme 

2. add nginx ingress controller
    * cd ./nginx-ingress + follow readme
 
3. setup cert-manager
   * cd ./cert-manager + follow readme

4. setup dashboard
   * cd ./kubernetes-dashboard + follow readme
 
5. setup longhorn for block storage
   * cd ./databases/longhorn + follow readme