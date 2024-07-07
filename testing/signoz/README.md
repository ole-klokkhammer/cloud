# https://signoz.io/docs/operate/configuration/
# https://github.com/signoz/charts/tree/main/charts/signoz
* helm repo add signoz https://charts.signoz.io
* helm install -n platform --create-namespace signoz signoz/signoz --values values.yaml
* helm upgrade -n platform signoz signoz/signoz --values values.yaml
* helm uninstall -n platform signoz