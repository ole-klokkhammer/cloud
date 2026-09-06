# LMS
https://lyrion.org/


## setup

## Disk
sudo zfs create -o compression=lz4 -o atime=off -o xattr=sa -o acltype=posixacl -o recordsize=4k ssd/appdata/lms

### lxc
- lxc profile create lms
- lxc profile edit lms
- lxc launch ubuntu:24.04 lms -p default -p lms
- lxc exec lms -- bash 


### installation
https://lyrion.org/getting-started/#__tabbed_1_3
https://github.com/lms-community/slimserver
https://lyrion.org/downloads/

sudo apt update && apt install -y curl
curl -LO https://downloads.lms-community.org/LyrionMusicServer_v9.1.0/lyrionmusicserver_9.1.0_amd64.deb
sudo apt install -f -y
dpkg -i lyrionmusicserver_9.1.0_amd64.deb


sudo systemctl enable lyrionmusicserver
sudo systemctl start lyrionmusicserver

### web ui
http://lms.home.lan:9000