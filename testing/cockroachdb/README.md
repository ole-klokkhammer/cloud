# README
https://medium.com/swlh/cockroachdb-on-a-raspberrypi-kubernetes-cluster-7b12a2e497e1

https://neilcameronwhite.medium.com/under-disk-pressure-34b5ba4284b6

# https://www.cockroachlabs.com/docs/v21.2/deploy-cockroachdb-with-kubernetes?filters=manual
# certificates
* mkdir certs my-safe-directory
* cockroach cert create-ca --certs-dir=certs --ca-key=my-safe-directory/ca.key
* cockroach cert create-client root --certs-dir=certs --ca-key=my-safe-directory/ca.key
* kubectl create secret generic cockroachdb.client.root --from-file=certs
* cockroach cert create-node --certs-dir=certs --ca-key=my-safe-directory/ca.key localhost 127.0.0.1 cockroachdb-public cockroachdb-public.default cockroachdb-public.default.svc.cluster.local *.cockroachdb *.cockroachdb.default *.cockroachdb.default.svc.cluster.local
* kubectl create secret generic cockroachdb.node --from-file=certs
* kubectl create -f deployment.yaml
* kubectl exec -it cockroachdb-0 -- /cockroach/cockroach init --certs-dir=/cockroach/cockroach-certs 

## SETUP
* kubectl create -f https://raw.githubusercontent.com/cockroachdb/cockroach/master/cloud/kubernetes/bring-your-own-certs/client.yaml
* kubectl exec -it cockroachdb-client-secure -- ./cockroach sql --certs-dir=/cockroach-certs --host=cockroachdb-public
* CREATE DATABASE homeassistant;
* CREATE USER ole WITH PASSWORD 'xxxx';
* GRANT admin TO ole;

## SETUP BACKUP SCHEDULE
CREATE SCHEDULE backup_schedule
FOR BACKUP INTO 's3://linole-cockroachdb/?AWS_ACCESS_KEY_ID=xxx&AWS_SECRET_ACCESS_KEY=xxx&AWS_ENDPOINT=https%3A%2F%2Fgateway.eu1.storjshare.io&AWS_REGION=eu-north-1'
RECURRING '@daily'
FULL BACKUP ALWAYS
WITH SCHEDULE OPTIONS first_run = 'now';

## DELETE ALL
* kubectl delete pods,statefulsets,services,poddisruptionbudget,jobs,rolebinding,clusterrolebinding,role,clusterrole,serviceaccount,alertmanager,prometheus,prometheusrule,serviceMonitor -l app=cockroachdb

# OLD
* kubectl create ns cockroachdb
* kubectl create -f ./deployment.yaml 
* kubectl create -f ./service.yaml
* kubectl create -f ./cluster-init.yaml 

# Database UI
## DBeaver
* has dockroach driver
## pgadmin
* kubectl apply -f ./pgadmin/secret.yaml

## Using the client
* exec in pod:
* cockroach sql --insecure --host=cockroachdb-public


## MONITORING
https://www.cockroachlabs.com/docs/v21.1/monitor-cockroachdb-kubernetes?filters=manual

##
https://upcloud.com/community/tutorials/install-cockroachdb-secure-database-cluster/


