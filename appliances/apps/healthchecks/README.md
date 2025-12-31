# healthchecks

- https://github.com/louislam/uptime-kuma?tab=readme-ov-file

## setup

### zfs
sudo zfs create -o quota=4G ssd/appdata/healthchecks
sudo zfs set recordsize=16K ssd/appdata/healthchecks
sudo zfs set atime=off ssd/appdata/healthchecks
sudo zfs set logbias=latency ssd/appdata/healthchecks
sudo zfs set compression=lz4 ssd/appdata/healthchecks

### LXC
- lxc profile create healthchecks
- lxc profile edit healthchecks
- lxc launch ubuntu:24.04 healthchecks -p default -p healthchecks
- lxc exec healthchecks -- bash


### Installation
sudo apt update
sudo apt install -y nodejs npm
npm install pm2 -g

cd /opt/healthchecks
git clone https://github.com/louislam/uptime-kuma.git
cd uptime-kuma
npm run setup


sudo nano /etc/systemd/system/healthchecks.service
-> add contents

sudo systemctl daemon-reload
sudo systemctl enable --now healthchecks
