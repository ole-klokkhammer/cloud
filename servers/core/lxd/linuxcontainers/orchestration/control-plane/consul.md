# consul 

## storage
sudo zfs create -o compression=lz4 -o atime=off ssd/appdata/consul
sudo zfs set logbias=latency ssd/appdata/consul

## setup

- lxc profile create consul-server
- lxc profile edit consul-server
- lxc launch ubuntu:24.04 consul-server -p default -p consul-server
- lxc exec consul-server -- bash
 
sudo apt update
sudo apt install -y gnupg lsb-release wget 
wget -O- https://apt.releases.hashicorp.com/gpg | sudo gpg --dearmor -o /usr/share/keyrings/hashicorp-archive-keyring.gpg
echo "deb [signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] https://apt.releases.hashicorp.com $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/hashicorp.list 
sudo apt update
sudo apt install -y consul


sudo nano /etc/consul.d/consul.hcl
--> add config

// consul keeps restarting with default config. add this
sudo systemctl edit consul
[Service]
Type=simple
TimeoutStartSec=300
Restart=on-failure
RestartSec=2
sudo systemctl daemon-reload
sudo systemctl restart consul
sudo systemctl status consul --no-pager -l

// start
sudo systemctl enable --now consul


## PFSENSE
dns resolver -> custom options:
server:
  include: /var/unbound/pfb_dnsbl.*conf

  local-zone: "consul." static
  forward-zone:
    name: "consul."
    forward-addr: 192.168.10.151#8600

---
dig @192.168.10.1 ntfy.service.consul