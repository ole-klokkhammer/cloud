# LXD

## caveats
we need kernel modules for vpn, but load them read only, and with a different mount inside the lxc to avoid symlink loops:

lib-modules:
  path: /mnt/lib_modules
  source: /lib/modules
  type: disk
  readonly: "true"

## setup

- lxc profile create nordvpn
- lxc profile edit nordvpn
- lxc launch ubuntu:24.04 nordvpn -p default -p nordvpn
- lxc exec nordvpn -- bash

### nordvpn 
https://nordvpn.com/download/linux/

sh <(curl -sSf https://downloads.nordcdn.com/apps/linux/install.sh)
nordvpn login --token <TOKEN>
nordvpn set killswitch on
nordvpn set autoconnect on
nordvpn set technology nordlynx
nordvpn connect

nordvpn whitelist add subnet 192.168.10.0/24
nordvpn set dns off   # let Nord handle DNS through VPN 

We need to specify by ip here as we dont use our local dns for security reasons

### install docker
sudo apt update
sudo apt install -y docker.io
sudo systemctl enable --now docker 

### docker-compose
sudo apt update
    sudo apt install ca-certificates curl gnupg -y
    sudo install -m 0755 -d /etc/apt/keyrings
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
    echo \
      "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
      $(lsb_release -cs) stable" | \
      sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
    sudo apt update
    sudo apt install docker-compose-plugin -y

### install systemd
lxc exec nordvpn -- bash
cd /docker/torrent-stack
sudo systemctl enable --now ./torrent-stack.service
 