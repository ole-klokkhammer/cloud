# GPU worker

## storage
sudo zfs create -o compression=lz4 -o atime=off ssd/llm/models
sudo zfs set logbias=latency ssd/llm/models
sudo zfs set recordsize=1M  ssd/llm/models 

## setup
- lxc profile create core-gpu
- lxc profile edit core-gpu
- lxc launch ubuntu:24.04 core-gpu -p default -p core-gpu
- lxc exec core-gpu -- bash

### docker


sudo nvidia-ctk runtime configure --runtime=docker
sudo systemctl restart docker

### install nomad client
sudo apt update
sudo apt install -y gnupg lsb-release
curl -fsSL https://apt.releases.hashicorp.com/gpg | sudo gpg --dearmor -o /usr/share/keyrings/hashicorp.gpg
echo "deb [signed-by=/usr/share/keyrings/hashicorp.gpg] https://apt.releases.hashicorp.com $(lsb_release -cs) main" \
  | sudo tee /etc/apt/sources.list.d/hashicorp.list
sudo apt update
sudo apt install -y nomad

sudo mkdir -p /etc/nomad.d
sudo nano /etc/nomad.d/nomad.hcl
sudo systemctl enable --now nomad 

### nomad nvidia device plugin
https://github.com/hashicorp/nomad-device-nvidia

sudo apt update
sudo apt install nomad-device-nvidia

sudo mkdir -p /opt/nomad/plugins
sudo ln -s /usr/bin/nomad-device-nvidia /opt/nomad/plugins/nomad-device-nvidia
 

## NUMA testing

### memory location
sudo  numastat -p $(pidof llama-server)
watch -n 0.5 "sudo  numastat -p $(pidof llama-server)"

### CPU localization
numactl --hardware
then verify cpu number with htop

### others
- numactl --cpunodebind=0 --membind=0
- numactl --interleave=all
