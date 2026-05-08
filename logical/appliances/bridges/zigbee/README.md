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
