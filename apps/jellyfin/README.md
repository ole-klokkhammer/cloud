# jellyfin

## preq
* sudo zfs create -o quota=500M k3s/jellyfin-data  

## setup
* kubectl create namespace jellyfin
* kubectl apply -f storage.yaml
* kubectl apply -f deployment.yaml
* kubectl apply -f service.yaml
