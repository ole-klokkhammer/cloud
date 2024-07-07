#  
* kubectl create -f https://download.elastic.co/downloads/eck/2.1.0/crds.yaml
* kubectl apply -f https://download.elastic.co/downloads/eck/2.1.0/operator.yaml
* kubectl -n elastic-system logs -f statefulset.apps/elastic-operator
* kubectl apply -f cluster.yaml
* kubectl get elasticsearch -w