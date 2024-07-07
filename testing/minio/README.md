# install krew RPI
* mkdir temp && cd temp
* VERSION=v0.4.3 curl -fsSLO https://github.com/kubernetes-sigs/krew/releases/download/v0.4.3/krew-linux_amd64.tar.gz
* tar zxvf krew-linux_amd64.tar.gz
* ./krew-linux_amd64 install krew
* Add to bashrc: export PATH="${KREW_ROOT:-$HOME/.krew}/bin:$PATH"

##  install minio

* kubectl krew install minio
* kubectl minio init
* create tenant in minio console

## minio console

* kubectl minio proxy



