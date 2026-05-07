

## ipvlan
set the cni parameters in the main config:
  cni_path = "/usr/lib/cni"
  cni_config_dir = "/etc/cni/net.d"

add configs
sudo nano /etc/cni/net.d/10-ipvlan.conflist

we need to run the dhcp
sudo /usr/lib/cni/dhcp daemon

and we need to set the network mode of the service
mode = "cni/ipvlan-lan" 

and the vm needs to set the nictype to physical or macvlan

## extra modules?
sudo modprobe bridge