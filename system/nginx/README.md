
##   
* https://ericsmasal.com/2021/08/nginx-ingress-load-balancer-and-metallb/
* helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
* helm install ingress-nginx  -n ingress-nginx --create-namespace --values ingress-nginx.yaml ingress-nginx/ingress-nginx  
* kubectl delete -A ValidatingWebhookConfiguration syntak-ingress-ingress-nginx-admission

#
NAME: ingress-nginx
LAST DEPLOYED: Sun Jun  5 13:07:43 2022
NAMESPACE: ingress-nginx
STATUS: deployed
REVISION: 1
TEST SUITE: None
NOTES:
The ingress-nginx controller has been installed.
It may take a few minutes for the LoadBalancer IP to be available.
You can watch the status by running 'kubectl --namespace ingress-nginx get services -o wide -w ingress-nginx-controller'

An example Ingress that makes use of the controller:
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
name: example
namespace: foo
spec:
ingressClassName: nginx
rules:
- host: www.example.com
http:
paths:
- pathType: Prefix
backend:
service:
name: exampleService
port:
number: 80
path: /
# This section is only required if TLS is to be enabled for the Ingress
tls:
- hosts:
- www.example.com
secretName: example-tls

If TLS is enabled for the Ingress, a Secret containing the certificate and key must also be provided:

apiVersion: v1
kind: Secret
metadata:
name: example-tls
namespace: foo
data:
tls.crt: <base64 encoded cert>
tls.key: <base64 encoded key>
type: kubernetes.io/tls