# nomad stateless

## create vm

- lxc profile create cloud-vm
- lxc profile edit cloud-vm
- lxc init ubuntu:24.04 cloud-0 --vm -p cloud-vm
- lxc start cloud-0
- lxc exec cloud-0 -- passwd ubuntu // set password
- copy ssh key to the host
  cat ~/.ssh/idXXXx.pub
  -> lxc console cloud-0 -> ~/.ssh/authorized_keys
- lxc console cloud-0

## install docker

sudo apt update
sudo apt install -y docker.io
sudo systemctl enable --now docker

## install podman

https://developer.hashicorp.com/nomad/plugins/drivers/podman

sudo apt-get update && sudo apt-get install -y podman wget gpg coreutils
wget -O- https://apt.releases.hashicorp.com/gpg | sudo gpg --dearmor -o /usr/share/keyrings/hashicorp-archive-keyring.gpg
echo "deb [signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] https://apt.releases.hashicorp.com $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/hashicorp.list
sudo apt-get update && sudo apt-get install -y nomad-driver-podman

## https://github.com/hashicorp/nomad-driver-podman

add to config:

```bash
plugin "nomad-driver-podman" {
  config {
    volumes {
      enabled      = true
      selinuxlabel = "z"
    }
  }
}
```

## install nomad client

sudo apt update && sudo apt-get -y install podman

### config

sudo mkdir -p /etc/nomad.d
sudo nano /etc/nomad.d/nomad.hcl
sudo systemctl enable --now nomad
