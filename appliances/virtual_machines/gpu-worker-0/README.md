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

### config
sudo mkdir -p /etc/nomad.d
sudo nano /etc/nomad.d/nomad.hcl
sudo systemctl enable --now nomad

## OOM memory management

we may need to cap arc caching to avoid spending too much ram

// cap ARC to 96 GiB
echo $((96*1024*1024*1024)) | sudo tee /sys/module/zfs/parameters/zfs_arc_max


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

7. Test ollama
mkdir -p ~/ollama

docker rm -f ollama 2>/dev/null || true
docker run -d --name ollama \
  --restart unless-stopped \
  --gpus all \
  -p 11434:11434 \
  -v ~/ollama:/root/.ollama \
  ollama/ollama:latest

docker exec -it ollama ollama list
docker exec -it ollama ollama run devstral-small-2:latest 


## temp testing
- ghcr.io/ggml-org/llama.cpp:full-cuda
- https://github.com/ggml-org/llama.cpp/blob/master/docs/docker.md
- https://huggingface.co/unsloth/Devstral-Small-2-24B-Instruct-2512-GGUF
 
### small
docker run --name llama-api \
  --restart unless-stopped \
  --network host \
  --gpus all \
  -v ~/llama-api/models:/models \
  ghcr.io/ggml-org/llama.cpp:full-cuda \
  --server \
  --host 0.0.0.0 \
  --port 8080 \
  -m /models/Devstral-Small-2-24B-Instruct-2512-Q4_K_M.gguf \
  -n 1024 \
  -t 12 \
  --n-gpu-layers -1 \
  -c 16384 \
  -b 512 \
  --temp 0.15

### large
docker run --name llama-api \
  --restart unless-stopped \
  --network host \
  --gpus all \
  -v ~/llama-api/models:/models \
  ghcr.io/ggml-org/llama.cpp:full-cuda \
  --server \
  --host 0.0.0.0 \
  --port 8080 \
  -m /models/Devstral-2-123B-Instruct-2512-Q4_K_M-00001-of-00002.gguf \
  -n 1024 \
  -t 24 \
  --n-gpu-layers 14 \
  -c 8096 \
  -b 512 \
  --temp 0.15