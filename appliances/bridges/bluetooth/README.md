# bluetooth

## setup 

## disable bluetooth on the host
Ensure the host is not using bluetooth

sudo systemctl stop bluetooth
sudo systemctl disable bluetooth
sudo systemctl mask bluetooth
  
sudo apt install -y rfkill
sudo rfkill unblock bluetooth

### get device ids
lsusb
Look for a line like: Bus 001 Device 004: ID 0b05:190e ASUSTek Computer, Inc. Zenbook Flip Bluetooth
VendorID: 0b05
ProductID: 190e

add in profile:
bluetooth:
  type: usb
  vendorid: "8087"
  productid: "0029"

## enable kvm support
On a Gigabyte Aorus B550, follow these steps to enable SVM:

Enter BIOS: Restart and tap the Delete key repeatedly.
Advanced Mode: Press F2 to switch to Advanced Mode (if not already there).
Navigate: Go to the Tweaker tab.
CPU Settings: Select Advanced CPU Settings.
Enable SVM: Find SVM Mode and set it to Enabled.
Enable IOMMU (Recommended for VMs):
Go to the Settings tab.
Select IOPorts.
Find IOMMU and set it to Enabled.
Save: Press F10 to Save and Exit.


sudo apt update && sudo apt install -y cpu-checker
kvm-ok
# Should now say: "KVM acceleration can be used"

### lxc
- lxc profile create bluetooth
- lxc profile edit bluetooth
- lxc launch ubuntu:24.04 bluetooth --vm --profile bluetooth
- lxc exec bluetooth -- passwd ubuntu // set password
- copy ssh key to the host
cat  ~/.ssh/idXXXx.pub
-> lxc console bluetooth -> ~/.ssh/authorized_keys
- lxc console bluetooth
- lxc exec bluetooth -- bash

### bluetooth
sudo apt update
sudo apt upgrade -y
sudo apt install -y bluez usbutils

// for bluetooth kernels
sudo apt install -y linux-modules-extra-$(uname -r)
sudo reboot

lsusb
// Check Bluetooth interface (should show hci0)
hciconfig -a

// start
sudo systemctl start bluetooth
sudo systemctl enable bluetooth


// test bluetooth
bluetoothctl
power on
agent on
default-agent
scan on
...
scan off
exit 