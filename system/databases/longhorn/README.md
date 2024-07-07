# Install

https://longhorn.io/docs/1.2.3/advanced-resources/deploy/customizing-default-settings/#using-helm

* on all nodes:
    * sudo apt-get install open-iscsi
* on all nodes that should have longhorn:
    * kubectl label nodes node0 node.longhorn.io/create-default-disk=true
    * kubectl label nodes node1 node.longhorn.io/create-default-disk=true
    * kubectl label nodes node2 node.longhorn.io/create-default-disk=true
    * kubectl label nodes node3 node.longhorn.io/create-default-disk=true
    * kubectl label nodes node4 node.longhorn.io/create-default-disk=false
* helm repo add longhorn https://charts.longhorn.io
* helm repo update
* curl -Lo values.yaml https://raw.githubusercontent.com/longhorn/charts/master/charts/longhorn/values.yaml
* sed -i 's/createDefaultDiskLabeledNodes: ~/createDefaultDiskLabeledNodes: true/g' values.yaml
* helm install longhorn longhorn/longhorn --namespace longhorn-system --create-namespace --values values.yaml
* kubectl -n longhorn-system get pod
* kubectl create -f ./service.yaml


## Backup to s3
* https://staging--longhornio.netlify.app/docs/0.8.1/snapshots-and-backups/backup-and-restore/set-backup-target/
* Get keys from user: https://us-east-1.console.aws.amazon.com/iam/home#/users/k3s-longhorn?section=security_credentials
* kubectl create -f ./secret

# UI

kubectl get svc --all-namespaces longhorn-frontend cluster-ip in browser 