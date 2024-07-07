## operator
* kubectl create -f https://raw.githubusercontent.com/pingcap/tidb-operator/master/manifests/crd.yaml
* kubectl get crd

# helm 
* helm repo add pingcap https://charts.pingcap.org/
* helm repo update
* kubectl create namespace tidb-admin
* helm install --namespace tidb-admin tidb-operator pingcap/tidb-operator --version v1.3.1

## cluster
* kubectl create namespace tidb-cluster
* kubectl create -f storageclass.yaml
* kubectl -n tidb-cluster apply -f tidb-cluster-amd64.yaml
* kubectl -n tidb-cluster apply -f tidb-cluster-arm64.yaml
* kubectl -n tidb-cluster apply -f tidb-monitor-amd64.yaml
* kubectl -n tidb-cluster apply -f tidb-monitor-arm64.yaml
* 