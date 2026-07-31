# # nomad
https://developer.hashicorp.com/nomad/docs/deploy

## storage
sudo zfs create -o compression=lz4 -o atime=off ssd/appdata/control-plane
sudo zfs set logbias=latency ssd/appdata/control-plane

## nomad

- lxc profile create nomad
- lxc profile edit nomad
- lxc launch ubuntu:24.04 nomad-server -p default -p nomad-server
- lxc exec nomad-server -- bash

### install
sudo apt-get update
sudo apt-get install -y wget gpg coreutils 
wget -qO- https://apt.releases.hashicorp.com/gpg | sudo gpg --dearmor -o /usr/share/keyrings/hashicorp.gpg
echo "deb [signed-by=/usr/share/keyrings/hashicorp.gpg] https://apt.releases.hashicorp.com $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/hashicorp.list
sudo apt-get update && sudo apt-get install -y nomad

### /etc/nomad.d/nomad.hcl
sudo nano /etc/nomad.d/nomad.hcl

### enable
sudo systemctl enable --now nomad
sudo systemctl status nomad --no-pager
