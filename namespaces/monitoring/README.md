# log db with timescaledb
* https://www.slingacademy.com/article/using-postgresql-with-timescaledb-for-logging-and-monitoring/
* https://www.slingacademy.com/article/how-to-implement-alerts-and-notifications-with-timescaledb/
* https://www.timescale.com/blog/build-an-application-monitoring-stack-with-timescaledb-telegraf-grafana

* kubectl create namespace monitoring

## Setup opentelemetry

## db https://docs.fluentbit.io/manual/pipeline/outputs/postgresql
* CREATE DATABASE monitoring;
* CREATE USER k3s_monitoring WITH PASSWORD 'xxx';
  ALTER DATABASE monitoring OWNER TO k3s_monitoring;
  GRANT ALL ON DATABASE monitoring TO k3s_monitoring;
* SELECT create_hypertable('k3s','time', migrate_data => true);
