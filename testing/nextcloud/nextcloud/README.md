# basic 
* https://github.com/vfreex/kube-nextcloud/tree/master/deploy/kubernetes/examples/kube-nextcloud
* https://github.com/acheaito/nextcloud-kubernetes/tree/master/nextcloud
* https://wiki.laxprad.ca:8443/tech/kubernetes-cluster/nextcloud-kubernetes
* https://matthewpalmer.net/kubernetes-app-developer/articles/php-fpm-nginx-kubernetes.html
* https://faun.pub/nextcloud-scale-out-using-kubernetes-93c9cac9e493
* CREATE DATABASE nextcloud;
* CREATE USER nextcloud WITH PASSWORD 'xxx';
* GRANT ALL ON DATABASE nextcloud TO xxx;
* kubectl create secret generic -n linole nextcloud-secrets \
  --from-literal=NEXTCLOUD_ADMIN_USER='xxx' \
  --from-literal=NEXTCLOUD_ADMIN_PASSWORD='xxx' \
  --from-literal=OBJECTSTORE_S3_HOST='gateway.storjshare.io' \
  --from-literal=OBJECTSTORE_S3_BUCKET='linole-nextcloud' \
  --from-literal=OBJECTSTORE_S3_KEY='xxx' \
  --from-literal=OBJECTSTORE_S3_SECRET='xxx' \
  --from-literal=REDIS_HOST='redis.default.svc.cluster.local' \
  --from-literal=REDIS_HOST_PORT='6379' \
  --from-literal=REDIS_HOST_PASSWORD='xxx' \
  --from-literal=POSTGRES_DB='xxx' \
  --from-literal=POSTGRES_USER='xxx' \
  --from-literal=POSTGRES_PASSWORD='xxx' \
  --from-literal=POSTGRES_HOST='timescaledb.default.svc.cluster.local'
  --from-literal=NEXTCLOUD_TRUSTED_DOMAINS='nextcloud.intern.linole.no'
  --from-literal=OVERWRITECLIURL='http://nextcloud.intern.linole.no'
  --from-literal=OVERWRITEHOST='nextcloud.intern.linole.no'
  --from-literal=OVERWRITEPROTOCOL='http' 
* kubectl create configmap nextcloud-nginx-config --from-file=./config -n linole
* kubectl create -f service.yaml
* kubectl create -f deployment.yaml 

 
# 
1. Get the nextcloud URL by running:

echo http://nextcloud.kube.home/

2. Get your nextcloud login credentials by running:

echo User:     admin
echo Password: $(kubectl get secret --namespace linole nextcloud -o jsonpath="{.data.nextcloud-password}" | base64 --decode)


# helm
* helm repo add nextcloud https://nextcloud.github.io/helm/
* helm repo update 
* helm install nextcloud --namespace linole -f values.yaml nextcloud/nextcloud
* helm upgrade nextcloud --namespace linole -f values.yaml nextcloud/nextcloud