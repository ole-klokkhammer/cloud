# HAOS
https://seanblanchfield.com/2023/05/home-assistant-os-in-lxd

## create haos image

- https://github.com/home-assistant/operating-system/releases/tag/16.3
- on host:
  - cd /tmp
  - mkdir haos-image
  - cd haos-image
  - wget https://github.com/home-assistant/operating-system/releases/download/16.3/haos_ova-16.3.qcow2.xz
  - xz -d haos_ova-*.qcow2.xz
  - cat << EOF > metadata.yaml 
architecture: x86_64
creation_date: 1624888256
properties:
  description: Home Assistant image
  os: Debian
  release: 16.3
EOF
  - tar -cvzf metadata.tar.gz metadata.yaml
  - lxc image import metadata.tar.gz disk.qcow2 --alias haos-16.3

### 
LXD uses the colon for remote:alias, so for local images, use a simple alias like haos or haos-16.3. Rename your alias if needed, then launch with that name.

## create vm
- lxc profile create homeassistant-vm 
- lxc profile edit homeassistant-vm 
- lxc init haos-16.3 homeassistant --vm -p homeassistant-vm -c security.secureboot=false
- lxc config device add homeassistant homeassistant-data disk source=/dev/zvol/ssd/appdata/homeassistant-zvol path=/config
- lxc start homeassistant
- lxc console homeassistant 


## first time, or restoring
- complete onboarding
- go to settings -> system -> storage
- move data dir to the attached homeassistant-data disk

## mounting on host and copying files
sudo mkdir /mnt/haos-zvol
sudo mount /dev/zvol/ssd/appdata/homeassistant-zvol /mnt/haos-zvol
sudo cp -r /path/to/source/* /mnt/haos-zvol/
sudo umount /mnt/haos-zvol