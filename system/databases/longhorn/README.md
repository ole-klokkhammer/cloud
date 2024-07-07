
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
- or:
- USER=<USERNAME_HERE>; PASSWORD=<PASSWORD_HERE>; echo "${USER}:$(openssl passwd -stdin -apr1 <<< ${PASSWORD})" >> auth
- kubectl -n longhorn-system create secret generic basic-auth --from-file=auth
- kubectl -n longhorn-system apply -f longhorn-ingress.yml


## Backup to s3
* https://staging--longhornio.netlify.app/docs/0.8.1/snapshots-and-backups/backup-and-restore/set-backup-target/
* Get keys from user: https://us-east-1.console.aws.amazon.com/iam/home#/users/k3s-longhorn?section=security_credentials
* kubectl create -f ./secret

# UI

kubectl get svc --all-namespaces  