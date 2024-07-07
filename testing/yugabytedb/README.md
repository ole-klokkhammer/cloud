# releases

https://github.com/YugaByte/yugabyte-db/releases

# docker

* docker buildx build --push --platform linux/amd64,linux/arm64/v8 -t 192.168.0.203:5000/yugabytedb:1.9.4 .

# helm
* ulimit -c unlimited
* ulimit -n 1048576
* helm repo add yugabytedb https://charts.yugabyte.com
* helm repo update
* kubectl create namespace yugabyte
* helm install yugabytedb yugabytedb/yugabyte --values ./values.yaml --namespace=yugabyte --wait

# docker image

https://gruchalski.com/posts/2021-06-15-yugabytedb-docker-image/
https://github.com/radekg/yugabyte-db-build-infrastructure/blob/master/.docker/yugabyte-db/Dockerfile