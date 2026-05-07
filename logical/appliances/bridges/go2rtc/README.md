# go2rtc

## setup 

### storage
sudo zfs create ssd/appdata/go2rtc
 
### lxc 
- lxc profile create go2rtc
- lxc profile edit go2rtc
- lxc launch ubuntu:24.04 go2rtc -p default -p go2rtc
- lxc exec go2rtc -- bash 
 

### install
sudo apt update
sudo apt install -y wget curl
sudo apt install -y ffmpeg

sudo useradd -r -s /usr/sbin/nologin go2rtc
sudo mkdir -p /opt/go2rtc
sudo chown go2rtc:go2rtc /opt/go2rtc

cd /opt/go2rtc
sudo -u go2rtc wget https://github.com/AlexxIT/go2rtc/releases/latest/download/go2rtc_linux_amd64
sudo -u go2rtc mv go2rtc_linux_amd64 go2rtc
sudo chmod +x go2rtc

sudo -u go2rtc nano /config/go2rtc.yaml 
---

sudo nano /etc/systemd/system/go2rtc.service
---


### access
http://go2rtc.home.lan:1984