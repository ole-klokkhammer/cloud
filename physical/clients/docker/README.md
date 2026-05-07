# docker 

## setup
sudo apt update
sudo apt install -y apt-transport-https ca-certificates curl software-properties-common   

curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin   

###
sudo usermod -aG docker $USER
newgrp docker


### On each Docker client that needs to push/pull:
lxc file pull core:container-registry/certs/domain.crt /tmp/domain.crt
sudo mkdir -p /etc/docker/certs.d/container-registry.home.lan:5000
sudo cp /tmp/domain.crt /etc/docker/certs.d/container-registry.home.lan:5000/ca.crt

### then on each server
lxc file pull core:container-registry/certs/domain.crt /tmp/domain.crt
lxc exec core:cloud-0 -- mkdir -p /etc/docker/certs.d/container-registry.home.lan:5000
lxc file push /tmp/domain.crt core:cloud-0/etc/docker/certs.d/container-registry.home.lan:5000/ca.crt