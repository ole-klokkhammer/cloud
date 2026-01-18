# nomad stateless

## create vm
- lxc profile create cloud-vm
- lxc profile edit cloud-vm
- lxc init ubuntu:24.04 cloud-0 --vm -p cloud-vm
- lxc start cloud-0
- lxc exec cloud-0 -- passwd ubuntu // set password
- copy ssh key to the host
cat  ~/.ssh/idXXXx.pub
-> lxc console cloud-0 -> ~/.ssh/authorized_keys
- lxc console cloud-0
 
## install docker
sudo apt update
sudo apt install -y docker.io
sudo systemctl enable --now docker

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

### container registry certs
lxc file pull core:container-registry/certs/domain.crt /tmp/domain.crt
lxc exec core:cloud-0 -- mkdir -p /etc/docker/certs.d/container-registry.home.lan:5000
lxc file push /tmp/domain.crt core:cloud-0/etc/docker/certs.d/container-registry.home.lan:5000/ca.crt