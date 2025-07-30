# rabbitmq
- https://www.rabbitmq.com/kubernetes/operator/install-operator.html
- https://github.com/bitnami/charts/blob/main/bitnami/rabbitmq/values.yaml
- https://docs.bitnami.com/virtual-machine/infrastructure/rabbitmq/administration/connect-remotely/
  
## setup operator
- https://www.rabbitmq.com/kubernetes/operator/quickstart-operator
* kubectl apply -f "https://github.com/rabbitmq/cluster-operator/releases/latest/download/cluster-operator.yml" 



## install cluster
* kubectl apply -f cluster.yaml

## login
* username is: admin  
* password:
  * kubectl get secret rabbitmq -n brokers -o jsonpath="{.data.rabbitmq-password}" | base64 --decode

## upgrade
* helm upgrade rabbitmq oci://registry-1.docker.io/bitnamicharts/rabbitmq-cluster-operator \
  --namespace brokers \
  -f values.yaml



## keycloak
- https://www.rabbitmq.com/docs/oauth2-examples-keycloak
- https://www.rabbitmq.com/docs/next/oauth2-examples#mqtt-protocol
- https://github.com/emmanuelgonz/nost_rabbitmq_keycloak
- https://github.com/rabbitmq/rabbitmq-server/tree/main/deps/rabbitmq_auth_backend_oauth2
- https://github.com/emmanuelgonz/nost_rabbitmq_keycloak/blob/main/conf/keycloak/rabbitmq.conf

### setup
Create a Client Scope:

Go to Client Scopes in Keycloak admin.
Click Create, name it rabbitmq.tag:management, save.
Assign Scope to Client:

Go to Clients > select your client (e.g., rabbitmq).
Under Client Scopes, add rabbitmq.tag:management to Default Client Scopes or Optional Client Scopes.


## anonymous login issues
* create a user: guest:guest and give it all privelieges.