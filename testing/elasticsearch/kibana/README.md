#
* kubectl apply -f deployment.yaml
* kubectl get kibana -w
* kubectl create -f service.yaml
* kubectl get secret elasticsearch-es-elastic-user -o=jsonpath='{.data.elastic}' | base64 --decode; echo