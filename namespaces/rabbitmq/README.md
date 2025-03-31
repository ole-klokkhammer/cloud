# Rabbitmq 
* https://www.rabbitmq.com/kubernetes/operator/install-operator.html
* https://www.rabbitmq.com/kubernetes/operator/using-operator
* helm repo add bitnami https://charts.bitnami.com/bitnami
* kubectl create namespace rabbitmq
* helm install -n rabbitmq rabbitmq bitnami/rabbitmq-cluster-operator
* kubectl apply -f cluster.yaml