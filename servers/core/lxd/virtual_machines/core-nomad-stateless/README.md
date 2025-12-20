# nomad stateless

## create vm
- lxc profile create nomad-stateless-vm
- lxc profile edit nomad-stateless-vm
- lxc init ubuntu:24.04 core-nomad-stateless --vm -p nomad-stateless-vm
- lxc start core-nomad-stateless
- lxc exec core-nomad-stateless -- passwd ubuntu // set password
- copy ssh key to the host
- lxc console core-nomad-stateless


## install inside vm
./nomad-client

sudo apt update
sudo apt install -y docker.io
sudo systemctl enable --now docker


## enable bridge kernel in vm
sudo modprobe bridge
echo bridge | sudo tee -a /etc/modules
sudo apt install -y containernetworking-plugins

## use built in docker bridge network mode
 
sudo usermod -aG docker nomad
sudo usermod -aG docker ubuntu
sudo systemctl restart docker
sudo systemctl restart nomad