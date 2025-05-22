# Apache Flink

## Flink Session Cluster

Using a session cluster here, as it allows us to use fewer resources.
<https://medium.com/@knoldus/flink-on-kubernetes-cf579582182b>

<https://nightlies.apache.org/flink/flink-docs-master/docs/deployment/resource-providers/standalone/kubernetes/>

kubectl create -f jobmanager-deployment.yaml
kubectl create -f taskmanager-deployment.yaml
kubectl create -f jobmanager-service.yaml
kubectl create -f jobmanager-rest-service.yaml

## Adding jobs

* Create the storage area to store the jobs. Jobs will be pushed to disk on that location - similar to how we do with hivemq extensions.
*

## Streams

 <https://sdtimes.com/how-to-build-a-multi-agent-orchestrator-using-flink-and-kafka-2/>
