# unifi

- https://help.ui.com/hc/en-us/articles/220066768-Updating-and-Installing-Self-Hosted-UniFi-Network-Servers-Linux
https://community.ui.com/questions/
- UniFi-OS-Server-Installation-Scripts-or-UniFi-Network-Application-Installation-Scripts-or-UniFi-Eas/ccbc7530-dd61-40a7-82ec-22b17f027776

## setup 
- lxc profile create unifi
- lxc profile edit unifi
- lxc launch ubuntu:24.04 unifi -p default -p unifi  
- lxc exec unifi -- bash
  - sudo apt update
    apt-get update; apt-get install ca-certificates curl -y
    curl -sO https://get.glennr.nl/unifi/install/install_latest/unifi-latest.sh && bash unifi-latest.sh
    sudo systemctl status mongod
    sudo systemctl enable mongod
    sudo systemctl start mongod
    sudo systemctl restart unifi