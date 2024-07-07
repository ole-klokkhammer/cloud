# 
* https://thenewstack.io/tutorial-configure-cloud-native-edge-infrastructure-with-k3s-calico-portworx/
* https://thenewstack.io/tutorial-install-and-configure-portworx-on-a-bare-metal-kubernetes-cluster/

## HOW TO
* install etcd cluster for storing state (not the k3s db)
* MAKE SURE the etcd cluster is in namespace: kube-system
* sudo mkdir -p /mnt/k3s/disk1/k3s/storage/etcd
* sudo chmod 771 /mnt/k3s/disk1/k3s/storage/etcd
* kubectl apply -f pv-etcd
* kubectl apply -f pvc-etcd
* kubectl get pv
* check that its bound: kubectl get pvc -n kube-system
* helm repo add bitnami https://charts.bitnami.com/bitnami
* helm repo update 
* helm install px-etcd bitnami/etcd --set replicaCount=4 --set auth.rbac.enabled=false --namespace=kube-system
* kubectl get pods -l app.kubernetes.io/name=etcd -n=kube-system
 