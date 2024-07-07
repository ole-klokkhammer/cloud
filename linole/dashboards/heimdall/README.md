# Heimdall

* kubectl create ns application-dashboard
* kubectl create -f ./deployment.yaml
* kubectl create -f ./service.yaml

kubectl cp ./heimdall/config application-dashboard/heimdall-0:/