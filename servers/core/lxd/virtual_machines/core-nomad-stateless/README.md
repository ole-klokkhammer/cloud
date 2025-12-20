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

sudo apt update
sudo apt install -y podman containernetworking-plugins

// enable podman rootless for the user
sudo loginctl enable-linger $USER

// logout and in
systemctl --user start podman.socket

podman info | grep rootless

// install nomad
./nomad-client 

## enable bridge kernel in vm
sudo modprobe bridge
echo bridge | sudo tee -a /etc/modules
sudo apt install -y containernetworking-plugins
