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


config
--- 

---


sudo systemctl enable --now consul