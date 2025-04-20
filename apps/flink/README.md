# Streams
* https://sdtimes.com/how-to-build-a-multi-agent-orchestrator-using-flink-and-kafka-2/


## Apache Flink
* https://nightlies.apache.org/flink/flink-kubernetes-operator-docs-stable/docs/try-flink-kubernetes-operator/quick-start/
* kubectl create namespace flink
* helm repo add flink-operator-repo https://downloads.apache.org/flink/flink-kubernetes-operator-1.11.0/
* helm install -n flink flink-kubernetes-operator flink-operator-repo/flink-kubernetes-operator -f helm-values.yaml
* helm upgrade -n flink flink-kubernetes-operator flink-operator-repo/flink-kubernetes-operator -f helm-values.yaml