# Makeplane plane

* https://developers.plane.so/self-hosting/methods/kubernetes
* kubectl create namespace plane
* DOMAIN_NAME=plane.linole.no
* helm repo add plane https://helm.plane.so/
* helm install plane-app plane/plane-enterprise \
  --create-namespace \
  --namespace plane \
  -f values.yaml \
  --timeout 10m \
  --wait \
  --wait-for-jobs