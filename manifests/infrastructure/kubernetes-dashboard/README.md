# how to 

# install:
- https://github.com/kubernetes/dashboard

- helm repo add kubernetes-dashboard https://kubernetes.github.io/dashboard/
- helm upgrade --install kubernetes-dashboard kubernetes-dashboard/kubernetes-dashboard \
--create-namespace \
--namespace kubernetes-dashboard \
--set kong.image.repository=kong \
--set kong.image.tag="3.9.0"
- faulty kong crash on reboot, use 3.9.0?
  - https://github.com/kubernetes/dashboard/issues/9955


## docs:
- https://github.com/kubernetes/dashboard/tree/master/docs

##  admin user config (https://github.com/kubernetes/dashboard/blob/master/docs/user/access-control/creating-sample-user.md)
* kubectl apply -f dashboard.admin-user.yaml
* kubectl apply -f dashboard.admin-user-role.yaml


## create token
- kubectl -n kubernetes-dashboard create token admin-user

## Getting a long-lived Bearer Token for ServiceAccount
- kubectl -n kubernetes-dashboard create token admin-user

## access dashboard
- kubectl -n kubernetes-dashboard port-forward svc/kubernetes-dashboard-kong-proxy 8443:443