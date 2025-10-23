# external secrets operator
* https://external-secrets.io/latest/introduction/getting-started/
* https://external-secrets.io/latest/provider/hashicorp-vault/

## setup
* helm repo add external-secrets https://charts.external-secrets.io
* helm repo update
* helm install external-secrets \
   external-secrets/external-secrets \
    -n external-secrets \
    --create-namespace
* kubectl apply store.yaml
