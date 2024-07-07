# mqtt-connector
* git clone https://github.com/openfaas/faas-netes.git
* helm template -n openfaas-mqtt-connector --namespace openfaas --values ./values.yaml ./faas-netes/chart/mqtt-connector/ --output-dir .
* kubectl apply -f ./mqtt-connector/templates/deployment.yaml
* kubectl logs deployment.apps/openfaas-mqtt-connector -n openfaas -f