#
* kubectl -n linole create configmap diun-config --from-file=./config 
* kubectl -n linole create -f ./deployment.yaml


# update configmap
* kubectl create configmap diun-config --from-file=./config -n linole --dry-run=client -o yaml | kubectl apply -f -