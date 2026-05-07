# NFS

## Setup
* sudo apt update
* sudo apt install nfs-kernel-server
* sudo systemctl enable nfs-server
* sudo systemctl start nfs-server


## Expose ZFS shares
* sudo zfs set sharenfs="on" hdd/music

## Expose regular shares
* sudo mkdir -p /export/music
* sudo chown nobody:nogroup /export/music
* sudo chmod 0777 /export/music
* sudo nano /etc/exports
* add  a line like: /export/music  *(rw,sync,no_subtree_check,no_root_squash)

## k3s example mount
https://github.com/yairk-create/k3s-nfs/blob/main/README.md

```yaml
apiVersion: v1
kind: PersistentVolume
metadata:
  name: torrent-music
spec:
  capacity:
    storage: 4Ti
  accessModes:
    - ReadWriteMany
  nfs:
    server: 192.168.10.2
    path: /hdd/music  
  persistentVolumeReclaimPolicy: Retain
  storageClassName: local-path
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: torrent-music-pvc
  namespace: apps
spec:
  storageClassName: local-path
  accessModes:
    - ReadWriteMany
  resources:
    requests:
      storage: 4Ti
  volumeName: torrent-music
---
```