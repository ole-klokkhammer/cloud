# GPU worker

## setup
- lxc profile create gpu-worker-vm
- lxc profile edit gpu-worker-vm
- lxc init ubuntu:24.04 gpu-worker-0 --vm -p gpu-worker-vm
- lxc start gpu-worker-0
- lxc exec gpu-worker-0 -- passwd ubuntu // set password
- copy ssh key to the host
cat  ~/.ssh/idXXXx.pub
-> lxc console gpu-worker-0 -> ~/.ssh/authorized_keys
- lxc console gpu-worker-0

## System Improvements
### Prevent double caching on host and in vm. On host:
sudo zfs set primarycache=metadata ssd/lxd/virtual-machines/gpu-worker-0.block

### ensure numa node location
We only have one socket, and two CCD, so 1 or 2 numa is the only viable option

limits.cpu: "16" 
limits.cpu.mode: host
limits.cpu.nodes: "0,1" # Pins VM to both physical NUMA nodes
limits.memory: "196GB"

# Run the container with memory interleaving
numactl --interleave=all docker run ....

test memory numa location


### We can also use hugepages to improve vm boot speed, but only use it for testing as it can cause instability
1. Reserve hugepages (e.g., for 196GB using 2MB pages):
Calculate: 196 * 1024 / 2 = 100352 pages
echo 100352 | sudo tee /proc/sys/vm/nr_hugepages

2. Update the LXD profile to use them:
lxc profile set gpu-worker-0 limits.memory.hugepages true


## install docker
sudo apt update
sudo apt install -y docker.io
sudo systemctl enable --now docker
sudo usermod -aG docker $USER

## install nomad client
sudo apt update
sudo apt install -y gnupg lsb-release
curl -fsSL https://apt.releases.hashicorp.com/gpg | sudo gpg --dearmor -o /usr/share/keyrings/hashicorp.gpg
echo "deb [signed-by=/usr/share/keyrings/hashicorp.gpg] https://apt.releases.hashicorp.com $(lsb_release -cs) main" \
  | sudo tee /etc/apt/sources.list.d/hashicorp.list
sudo apt update
sudo apt install -y nomad

### nomad nvidia device plugin
https://github.com/hashicorp/nomad-device-nvidia

sudo apt update
sudo apt install nomad-device-nvidia

sudo mkdir -p /opt/nomad/plugins
sudo ln -s /usr/bin/nomad-device-nvidia /opt/nomad/plugins/nomad-device-nvidia

add to config:
plugin_dir = "/opt/nomad/plugins"
plugin "nomad-device-nvidia" {
  config {
    enabled = true
  }
}

### config
sudo mkdir -p /etc/nomad.d
sudo nano /etc/nomad.d/nomad.hcl
sudo systemctl enable --now nomad 


## gpu passthrough

1. settings
- enable iommu in bios
- enable virtualization: svm mode -> on
- sudo nano /etc/default/grub
      - GRUB_CMDLINE_LINUX_DEFAULT="...... amd_iommu=on iommu=pt"
- sudo update-grub
- sudo reboot
- verify:
  - `dmesg | grep -iE 'amd-vi|iommu|pt|passthrough'`
  - `cat /proc/cmdline`

2. find the gpu
ubuntu@core:~$ lspci -nn | grep -E "VGA|3D|Audio"
45:00.0 VGA compatible controller [0300]: ASPEED Technology, Inc. ASPEED Graphics Family [1a03:2000] (rev 41)
c1:00.0 VGA compatible controller [0300]: NVIDIA Corporation Device [10de:2d04] (rev a1)
c1:00.1 Audio device [0403]: NVIDIA Corporation Device [10de:22eb] (rev a1)
c2:00.0 Non-Volatile memory controller [0108]: Sandisk Corp SanDisk Ultra 3D / WD Blue SN550 NVMe SSD [15b7:5009] (rev 01)
c3:00.0 Non-Volatile memory controller [0108]: Sandisk Corp SanDisk Ultra 3D / WD Blue SN550 NVMe SSD [15b7:5009] (rev 01)
ubuntu@core:~$ GPU="0000:c1:00.0"
ubuntu@core:~$ readlink -f /sys/bus/pci/devices/$GPU/iommu_group
/sys/kernel/iommu_groups/77
ubuntu@core:~$ ls -l "$(readlink -f /sys/bus/pci/devices/$GPU/iommu_group)/devices" 

3. Add device to vm
- lxc stop gpu-worker-0
- lxc config device add gpu-worker-0 gpu pci address=0000:c1:00.0
- lxc config device add gpu-worker-0 gpu-audio pci address=0000:c1:00.1
- lxc start gpu-worker-0

4. Add drivers inside vm
sudo apt update
sudo apt install -y ubuntu-drivers-common
sudo systemd-hwdb update
sudo udevadm trigger
<!-- sudo ubuntu-drivers autoinstall -->
sudo reboot
nvidia-smi

5. configure nvidia container toolkit for docker 
https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html
sudo apt-get update && sudo apt-get install -y --no-install-recommends \
   curl \
   gnupg2
curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg \
  && curl -s -L https://nvidia.github.io/libnvidia-container/stable/deb/nvidia-container-toolkit.list | \
    sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' | \
    sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list
sudo apt-get update
export NVIDIA_CONTAINER_TOOLKIT_VERSION=1.18.1-1
sudo apt-get install -y \
    nvidia-container-toolkit=${NVIDIA_CONTAINER_TOOLKIT_VERSION} \
    nvidia-container-toolkit-base=${NVIDIA_CONTAINER_TOOLKIT_VERSION} \
    libnvidia-container-tools=${NVIDIA_CONTAINER_TOOLKIT_VERSION} \
    libnvidia-container1=${NVIDIA_CONTAINER_TOOLKIT_VERSION} 

sudo nvidia-ctk runtime configure --runtime=docker
sudo systemctl restart docker

6. verify
docker run --rm --gpus all nvidia/cuda:12.4.1-base-ubuntu22.04 nvidia-smi
