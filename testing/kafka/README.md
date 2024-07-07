# https://strimzi.io/quickstarts/
* kubectl create ns kafka
* kubectl create -f "https://strimzi.io/install/latest?namespace=kafka" -n kafka
* kubectl get pods -n kafka -w
* kubectl apply -f cluster.yaml
* kubectl apply -f service.yaml


## debugging
* kubectl port-forward -n kafka kafka-cluster-zookeeper-0 2181:2181
* kubectl port-forward -n kafka kafka-cluster-kafka-bootstrap 9092:9092