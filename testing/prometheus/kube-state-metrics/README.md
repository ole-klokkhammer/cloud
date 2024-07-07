# https://devopscube.com/setup-kube-state-metrics/
* git clone https://github.com/devopscube/kube-state-metrics-configs.git
* kubectl apply -f kube-state-metrics-configs/
* kubectl get deployments kube-state-metrics -n kube-system
* scrape config is already set in prometheus configmap
* 