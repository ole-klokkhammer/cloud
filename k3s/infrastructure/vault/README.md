# hashicorp vault

## zfs
* sudo zfs create -o quota=5G k3s/vault-data  

## setup

* helm repo add hashicorp https://helm.releases.hashicorp.com
* helm repo update
* helm upgrade --install vault hashicorp/vault -n vault --create-namespace -f values.yaml

## upgrade
* helm upgrade --install vault hashicorp/vault -n vault --create-namespace -f values.yaml

