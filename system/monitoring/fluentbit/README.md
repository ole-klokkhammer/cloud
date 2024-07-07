#  

* kubectl create -f rbac.yaml
* kubectl create configmap fluentbit-config --from-file=./config -n default
* kubectl create -f deployment.yaml

# update configmap
* kubectl create configmap fluentbit-config --from-file=./config -n default --dry-run=client -o yaml | kubectl apply -f -

https://docs.timescale.com/api/latest/hypertable/drop_chunks/#drop-chunks

# timescaledb

* CREATE DATABASE logdb; 
* CREATE USER k3s_log WITH PASSWORD 'xxxx'; 
* GRANT ALL PRIVILEGES ON DATABASE sysdb TO kubernetes_log; 
* GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public to kubernetes_log; 
* GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public to kubernetes_log; 
* GRANT ALL PRIVILEGES ON ALL FUNCTIONS IN SCHEMA public to kubernetes_log; 
* SELECT create_hypertable('k3s','time', migrate_data => true); 
* SELECT show_chunks('kubernetes');

# data retention

* https://docs.timescale.com/timescaledb/latest/how-to-guides/data-retention/create-a-retention-policy/
* SELECT add_retention_policy('conditions', INTERVAL '3 days');
* SELECT drop_chunks('kubernetes', INTERVAL '1 week');
* SELECT * FROM timescaledb_information.job_stats;
* SELECT * FROM timescaledb_information.jobs;