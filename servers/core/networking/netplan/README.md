# networking

## enable 2.5gbit
sudo ethtool -s enp66s0f0 advertise 0x1800000001028
sudo ethtool -s enp66s0f1 advertise 0x1800000001028

## bridge mode networking

- sudo nano /etc/netplan/50-cloud-init > add in 50-cloud-init.yaml
- sudo netplan generate
- sudo netplan apply