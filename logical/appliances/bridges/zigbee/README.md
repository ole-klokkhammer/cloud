# zigbee

## setup 

### storage

sudo lvcreate -L 1G -n zigbee2mqtt ubuntu-vg 
sudo mkfs.btrfs /dev/ubuntu-vg/zigbee2mqtt 


### get device ids
lsusb
Look for a line like: Bus 001 Device 004: ID 0b05:190e ASUSTek Computer, Inc. Zenbook Flip Bluetooth
VendorID: 0b05
ProductID: 190e

add in profile:
zigbee-usb:
  type: usb
  vendorid: "1a86"
  productid: "7523"
zigbee-serial:
  path: /dev/ttyUSB0
  type: unix-char

### lxc 
- lxc profile create zigbee
- lxc profile edit zigbee
- lxc launch ubuntu:24.04 zigbee -p default -p zigbee
- lxc exec zigbee -- bash 

### zigbee stick setup
https://support.electrolama.com/radio-docs/zigbee2mqtt/


### zigbee2mqtt
https://www.zigbee2mqtt.io/guide/installation/01_linux.html

// run without data dir attached

sudo apt-get install -y curl
sudo curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash -
sudo apt-get install -y nodejs git make g++ gcc libsystemd-dev
corepack enable 
node --version  # Should output V20.x, V22.X 
sudo mkdir /opt/zigbee2mqtt
sudo chown -R ${USER}: /opt/zigbee2mqtt 
git clone --depth 1 https://github.com/Koenkk/zigbee2mqtt.git /opt/zigbee2mqtt

cd /opt/zigbee2mqtt
pnpm install --frozen-lockfile

usermod -aG dialout ubuntu

// Create a systemctl configuration file for Zigbee2MQTT
sudo nano /etc/systemd/system/zigbee2mqtt.service
....

sudo systemctl enable zigbee2mqtt
sudo systemctl start zigbee2mqtt