#
* kubectl create configmap diun-mqtt-config --from-file=./config -n linole 
* kubectl create -f ./deployment.yaml


# update configmap
* kubectl create configmap diun-config --from-file=./config -n linole --dry-run=client -o yaml | kubectl apply -f -