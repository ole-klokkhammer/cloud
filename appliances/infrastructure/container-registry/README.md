# container registry
https://github.com/distribution/distribution

## setup
https://distribution.github.io/distribution/

### lxc
- lxc profile create container-registry
- lxc profile edit container-registry
- lxc launch ubuntu:24.04 container-registry -p default -p container-registry
- lxc exec container-registry -- bash 

### installation

sudo apt update
sudo apt upgrade -y

mkdir ~/tmp
cd ~/tmp
wget https://github.com/distribution/distribution/releases/download/v3.0.0/registry_3.0.0_linux_amd64.tar.gz
tar xzf registry_3.0.0_linux_amd64.tar.gz
sudo mv registry /usr/local/bin/

mkdir /etc/docker-registry
sudo nano /etc/docker-registry/config.yml
--- 

sudo nano /etc/systemd/system/docker-registry.service
---

sudo useradd -r -s /bin/false registry
sudo mkdir -p /var/lib/registry /etc/docker-registry
sudo chown registry:registry /var/lib/registry
sudo systemctl enable --now docker-registry

### ssl
lxc exec container-registry -- bash
sudo mkdir -p /certs 
cd /certs
openssl req -newkey rsa:4096 -nodes -sha256 \
  -keyout domain.key -x509 -days 365 \
  -out domain.crt \
  -subj "/CN=container-registry.home.lan" \
  -addext "subjectAltName=DNS:container-registry.home.lan"

sudo chown registry:registry /certs/domain.key /certs/domain.crt
sudo chmod 600 /certs/domain.key
sudo chmod 644 /certs/domain.crt

sudo systemctl restart docker-registry

### client setup
# On each Docker client that needs to push/pull:
lxc file pull core:container-registry/certs/domain.crt /tmp/domain.crt
sudo mkdir -p /etc/docker/certs.d/container-registry.home.lan:5000
sudo cp /tmp/domain.crt /etc/docker/certs.d/container-registry.home.lan:5000/ca.crt
 