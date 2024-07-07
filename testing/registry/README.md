# SETUP

* sudo cp ./registries.yaml /etc/rancher/k3s/
* sudo scp ./registries.yaml ubuntu@192.168.10.201:/etc/rancher/k3s/
* sudo scp ./registries.yaml ubuntu@192.168.10.202:/etc/rancher/k3s/
* sudo scp ./registries.yaml ubuntu@192.168.10.203:/etc/rancher/k3s/
* reload k3s service on all

## optional:

* edit /etc/docker/daemon.json
    * {
      "insecure-registries" : ["192.168.0.203:5000"]
      }
* reload docker daemon