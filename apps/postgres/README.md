# postgres

- docker run -i --rm postgres cat /usr/share/postgresql/postgresql.conf.sample > postgres.conf
- kubectl create namespace postgres
- kubectl create secret generic -n postgres postgres-secrets --from-env-file=.env
- kubectl create configmap postgres-config --from-file=main-config=postgres.conf -n postgres
- kubectl apply -f service.yaml
- kubectl apply -f deployment.yaml

## timescale
* https://www.timescale.com/ai/solutions/agentic-applications?bb=220956

## databases
-- Create a new database for linole 
CREATE DATABASE linole;