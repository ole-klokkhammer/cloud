# go2rtc

* https://github.com/AlexxIT/go2rtc/wiki/Hardware-acceleration
* https://github.com/AlexxIT/go2rtc/tree/master/internal/app

## setup
* kubectl create namespace go2rtc
* kubectl create secret generic -n go2rtc  go2rtc-secrets --from-env-file=.env
* kubectl apply -f deployment.yaml
* kubectl apply -f service.yaml

