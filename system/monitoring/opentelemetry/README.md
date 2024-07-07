# opentelemetry-operator
* helm repo add open-telemetry https://open-telemetry.github.io/opentelemetry-helm-charts
* helm repo update
* helm install opentelemetry-operator open-telemetry/opentelemetry-operator

# https://github.com/open-telemetry/opentelemetry-collector
# https://github.com/open-telemetry/opentelemetry-helm-charts
# https://github.com/open-telemetry/opentelemetry-collector-contrib

# opentelemetry-collector
* kubectl create configmap otel-collector-config --from-file=./config -n default
* kubectl create -f rbac.yaml
* kubectl create -f daemonset.yaml
* kubectl create -f service.yaml
* 
# update configmap
* kubectl create configmap otel-collector-config --from-file=./config -n default --dry-run=client -o yaml | kubectl apply -f -