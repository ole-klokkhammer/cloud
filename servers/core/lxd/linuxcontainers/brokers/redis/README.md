# redis
https://github.com/hivemq/hivemq-community-edition/wiki/Configuration

## setup

- lxc profile create redis
- lxc profile edit redis
- lxc launch ubuntu:24.04 redis -p default -p redis

## install docker
sudo apt update
sudo apt install docker.io -y

## install nomad client
sudo apt update
sudo apt install -y gnupg lsb-release
curl -fsSL https://apt.releases.hashicorp.com/gpg | sudo gpg --dearmor -o /usr/share/keyrings/hashicorp.gpg
echo "deb [signed-by=/usr/share/keyrings/hashicorp.gpg] https://apt.releases.hashicorp.com $(lsb_release -cs) main" \
  | sudo tee /etc/apt/sources.list.d/hashicorp.list
sudo apt update
sudo apt install -y nomad

### config
sudo mkdir -p /etc/nomad.d
sudo nano /etc/nomad.d/nomad.hcl
sudo systemctl enable --now nomad