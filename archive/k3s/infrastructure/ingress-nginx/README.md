
##   
* https://ericsmasal.com/2021/08/nginx-ingress-load-balancer-and-metallb/
* helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
* helm upgrade --install ingress-nginx ingress-nginx \
  --repo https://kubernetes.github.io/ingress-nginx \
  --namespace ingress-nginx --create-namespace
 