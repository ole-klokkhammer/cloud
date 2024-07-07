https://rancher.com/docs/k3s/latest/en/installation/kube-dashboard/


GITHUB_URL=https://github.com/kubernetes/dashboard/releases
VERSION_KUBE_DASHBOARD=$(curl -w '%{url_effective}' -I -L -s -S ${GITHUB_URL}/latest -o /dev/null | sed -e 's|.*/||')
kubectl create -f https://raw.githubusercontent.com/kubernetes/dashboard/${VERSION_KUBE_DASHBOARD}/aio/deploy/recommended.yaml

## 
* kubectl apply -f dashboard.admin-user.yaml
* kubectl apply -f dashboard.admin-user-role.yaml
* kubectl edit service/kubernetes-dashboard -n kubernetes-dashboard
  * change to type: LoadBalancer
  * 


## cert manager
GITHUB_URL=https://github.com/jetstack/cert-manager/releases
VERSION_CERT_MANAGER=$(curl -w '%{url_effective}' -I -L -s -S ${GITHUB_URL}/latest -o /dev/null | sed -e 's|.*/||')
kubectl apply -f https://github.com/jetstack/cert-manager/releases/download/${VERSION_CERT_MANAGER}/cert-manager.yaml

https://wildwolf.name/how-to-expose-kubernetes-dashboard-over-https/