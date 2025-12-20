# nomad
 

## setup

sudo apt update
sudo apt install -y gnupg lsb-release
curl -fsSL https://apt.releases.hashicorp.com/gpg | sudo gpg --dearmor -o /usr/share/keyrings/hashicorp.gpg
echo "deb [signed-by=/usr/share/keyrings/hashicorp.gpg] https://apt.releases.hashicorp.com $(lsb_release -cs) main" \
  | sudo tee /etc/apt/sources.list.d/hashicorp.list
sudo apt update
sudo apt install -y nomad 

## config
sudo mkdir -p /etc/nomad.d
sudo nano /etc/nomad.d/nomad.hcl
---
---
sudo systemctl enable --now nomad

## cni bridge plugin
sudo apt update
sudo apt install -y containernetworking-plugins
sudo mkdir -p /opt/cni
sudo ln -s /usr/lib/cni /opt/cni/bin
sudo systemctl restart docker
sudo systemctl restart nomad

## extra modules
sudo modprobe bridge
echo bridge | sudo tee -a /etc/modules