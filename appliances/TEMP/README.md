lxc launch ubuntu:24.04 unifi -p default -p unifi
lxc exec unifi -- bash
apt-get update && apt-get install ca-certificates curl -y
curl -sO https://get.glennr.nl/unifi/install/install_latest/unifi-latest.sh && bash unifi-latest.sh
