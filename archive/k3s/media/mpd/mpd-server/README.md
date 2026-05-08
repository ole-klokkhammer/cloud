# mpd

https://github.com/uriel1998/docker-music-streaming

## setup volume
Use volumeMode: Block for ZVOLs
Use volumeMode: Filesystem for datasets 

* sudo zfs create -o quota=5G k3s/mpd-data  
* sudo zfs list -o name,volsize,used,available k3s/homeassistant-data

## build
* build if necessary

## setup
* kubectl -n apps create configmap mpd-server-config --from-file=config
* kubectl apply -f storage.yaml
* kubectl apply -f deployment.yaml
* kubectl apply -f service.yaml
* 