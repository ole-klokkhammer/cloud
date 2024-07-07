#  https://devopscube.com/setup-prometheus-monitoring-on-kubernetes/

* kubectl create namespace monitoring
* kubectl create -f clusterrole.yaml
* kubectl create -f configmap.yaml
* kubectl create  -f deployment.yaml 

## continue with subfolders