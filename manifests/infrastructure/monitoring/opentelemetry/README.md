# opentelemetry-operator 
# https://github.com/open-telemetry/opentelemetry-collector
# https://github.com/open-telemetry/opentelemetry-helm-charts
# https://github.com/open-telemetry/opentelemetry-collector-contrib

# opentelemetry-collector
* https://opentelemetry.io/docs/platforms/kubernetes/collector/components/#filelog-receiver
* kubectl create configmap otel-collector-config --from-file=./config -n monitoring
* kubectl create -f rbac.yaml
* kubectl create -f deployment.yaml
* kubectl create -f service.yaml
* 
# update configmap
* kubectl create configmap otel-collector-config --from-file=config.yaml -n monitoring --dry-run=client -o yaml | kubectl apply -f -

# kafka exporter
* https://github.com/open-telemetry/opentelemetry-collector-contrib/blob/main/exporter/kafkaexporter/README.md