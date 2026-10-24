# zot - container registry
https://github.com/project-zot/zot

## setup
https://zotregistry.dev/

### lxc
lxc profile create zot
lxc profile edit zot
lxc launch ubuntu:24.04 zot -p default -p zot
lxc exec zot -- bash 

### installation
https://zotregistry.dev/v2.1.17/install-guides/install-guide-linux/

sudo apt update
sudo apt upgrade -y

sudo wget -O /usr/bin/zot https://github.com/project-zot/zot/releases/download/v2.1.17/zot-linux-amd64
sudo chmod +x /usr/bin/zot
sudo chown root:root /usr/bin/zot

nano /etc/zot/config.json

htpasswd -bnB myUserName myPassword > /etc/zot/htpasswd
mkdir /var/log/zot
sudo zot verify /etc/zot/config.json

### pfsense
add to backend pass thru:

http-request set-header X-Forwarded-Proto https
http-request set-header X-Forwarded-Port 443