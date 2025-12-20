# nomad stateless

## create vm
- lxc profile create nomad-stateless-vm
- lxc profile edit nomad-stateless-vm
- lxc init ubuntu:24.04 core-nomad-stateless --vm -p nomad-stateless-vm
- lxc start core-nomad-stateless
- lxc exec core-nomad-stateless -- passwd ubuntu // set password
- copy ssh key to the host
- lxc console core-nomad-stateless


## install podman

sudo apt update
sudo apt install -y podman containernetworking-plugins

// enable podman rootless for the user
sudo loginctl enable-linger $USER

// logout and in
systemctl --user start podman.socket

podman info | grep rootless
 

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

### podman config
https://developer.hashicorp.com/nomad/plugins/drivers/podman

sudo apt-get update && \
  sudo apt-get install wget gpg coreutils
wget -O- https://apt.releases.hashicorp.com/gpg | sudo gpg --dearmor -o /usr/share/keyrings/hashicorp-archive-keyring.gpg
echo "deb [signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] https://apt.releases.hashicorp.com $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/hashicorp.list
sudo apt-get update && sudo apt-get install -y nomad-driver-podman

## ipvlan
set the cni parameters in the main config:
  cni_path = "/usr/lib/cni"
  cni_config_dir = "/etc/cni/net.d"

add configs
sudo nano /etc/cni/net.d/10-ipvlan.conflist

we need to run the dhcp
sudo /usr/lib/cni/dhcp daemon

and we need to set the network mode of the service
mode = "cni/ipvlan-lan" 

and the vm needs to set the nictype to physical or macvlan

## extra modules?
sudo modprobe bridge