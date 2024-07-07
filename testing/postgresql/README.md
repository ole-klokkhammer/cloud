#  

* kubectl create ns postgres
* kubectl apply -f pvc.yaml
* kubectl apply -f configmap.yaml
* kubectl apply -f deployment.yaml
* kubectl apply -f service.yaml



## Helm
* helm repo add bitnami https://charts.bitnami.com/bitnami
* helm repo update
* kubectl create ns postgres
* helm install postgres-ha bitnami/postgresql-ha --values ./helm/values.yaml --namespace=postgres