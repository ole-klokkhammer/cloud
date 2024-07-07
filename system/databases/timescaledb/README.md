#  
* git clone https://github.com/timescale/timescaledb-kubernetes.git
* kubectl create secret generic timescaledb-credentials \
  --from-literal=PATRONI_SUPERUSER_PASSWORD='xxx' \
  --from-literal=PATRONI_REPLICATION_PASSWORD='xxx' \
  --from-literal=PATRONI_admin_PASSWORD='xxx'
* openssl genrsa -out tls.key
* openssl req -new -key tls.key -out tls.csr
* openssl x509 -req -days 365 -in tls.csr -signkey tls.key -out tls.crt
* kubectl create secret generic timescaledb-certificate \
  --from-file=tls.crt \
  --from-file=tls.key
* kubectl create secret generic timescaledb-pgbackrest \
  --from-literal=PGBACKREST_REPO1_S3_REGION='eu-north-1' \
  --from-literal=PGBACKREST_REPO1_S3_KEY='xxxx' \
  --from-literal=PGBACKREST_REPO1_S3_KEY_SECRET='xxxx' \
  --from-literal=PGBACKREST_REPO1_S3_BUCKET='xxx' \
  --from-literal=PGBACKREST_REPO1_S3_ENDPOINT='xxx' 
* helm install timescaledb ./timescaledb-kubernetes/charts/timescaledb-single -f values.yaml
* helm upgrade timescaledb ./timescaledb-kubernetes/charts/timescaledb-single -f values.yaml

## Accessing database locally
* Get the password for access node
* PGPASSWORD_POSTGRES=$(kubectl get secret --namespace default timescale-db-timescaledb-access -o jsonpath="{.data.password-superuser}" | base64 --decode)
* Get the name of the access node pod
* ACCESS_POD=$(kubectl get pod -o name -n default -l role=master)
* Start a port forward from the access node
* kubectl port-forward $ACCESS_POD 5432:5432 -n=default


# creating stuff

* CREATE DATABASE sysdb;
* CREATE USER kubernetes_log WITH PASSWORD 'xxxx';
* GRANT ALL ON DATABASE sysdb TO kubernetes_log;

#
To get your password for superuser run:

    # superuser password
    PGPASSWORD_POSTGRES=$(kubectl get secret --namespace default timescaledb-credentials -o jsonpath="{.data.PATRONI_SUPERUSER_PASSWORD}" | base64 --decode)

    # admin password
    PGPASSWORD_ADMIN=$(kubectl get secret --namespace default timescaledb-credentials -o jsonpath="{.data.PATRONI_admin_PASSWORD}" | base64 --decode)

To connect to your database, choose one of these options:

1. Run a postgres pod and connect using the psql cli:
   # login as superuser
   kubectl run -i --tty --rm psql --image=postgres \
   --env "PGPASSWORD=$PGPASSWORD_POSTGRES" \
   --command -- psql -U postgres \
   -h timescaledb.default.svc.cluster.local postgres

   # login as admin
   kubectl run -i --tty --rm psql --image=postgres \
   --env "PGPASSWORD=$PGPASSWORD_ADMIN" \
   --command -- psql -U admin \
   -h timescaledb.default.svc.cluster.local postgres

2. Directly execute a psql session on the master node

   MASTERPOD="$(kubectl get pod -o name --namespace default -l release=timescaledb,role=master)"
   kubectl exec -i --tty --namespace default ${MASTERPOD} -- psql -U postgres

# uninstall

* helm uninstall timescaledb 


# data retention
SELECT add_retention_policy('conditions', INTERVAL '24 hours');

# sessions
SELECT pg_terminate_backend(pg_stat_activity.pid)
FROM pg_stat_activity
WHERE pg_stat_activity.datname = 'nextcloud'
AND pid <> pg_backend_pid();
