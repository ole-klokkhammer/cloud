
# mount disk to be used
sudo fdisk -l
sudo fdisk /dev/<disk>
sudo mkfs.ext4 /dev/<disk>
sudo mkdir /mnt/longhorn
sudo nano /etc/fstab
-- UUID="..." /mnt/disk1 ext4 nosuid,nodev,nofail,x-gvfs-show 0 0

# install
* on all nodes:
  * sudo apt-get install open-iscsi
* helm repo add longhorn https://charts.longhorn.io
* helm repo update
* helm install longhorn longhorn/longhorn --namespace longhorn-system --create-namespace --version 1.6.2

# ui https://longhorn.io/docs/1.6.2/deploy/accessing-the-ui/longhorn-ingress/
- access with proxy: kubectl port-forward -n longhorn-system svc/longhorn-frontend 8080:80 


## Backup to s3
* create access key in storj
* apiVersion: v1
  kind: Secret
  metadata:
  name: longhorn-storj-backups
  namespace: longhorn-system
  type: Opaque
  stringData:
  AWS_ACCESS_KEY_ID: xxxx
  AWS_ENDPOINTS: https://gateway.storjshare.io/
  AWS_SECRET_ACCESS_KEY: ccxxxcc
* set backup target credential secret in ui to: longhorn-storj-backups
* set backup target in ui to: s3://<bucketname>@eu1/