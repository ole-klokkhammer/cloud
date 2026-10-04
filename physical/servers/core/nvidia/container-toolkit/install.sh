#!/bin/bash
# nvidia-container-toolkit (root host) + CDI spec for rootless podman.
# Idempotent; safe to re-run. Run on core as a password-sudo user (ubuntu).
#
# https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html

set -euo pipefail

export NVIDIA_CONTAINER_TOOLKIT_VERSION=1.20.1-1 

sudo apt-get update
sudo apt-get install -y --no-install-recommends ca-certificates curl gnupg2

curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey \
  | sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg
curl -fsSL https://nvidia.github.io/libnvidia-container/stable/deb/nvidia-container-toolkit.list \
  | sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' \
  | sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list

sudo apt-get update
sudo apt-get install -y \
    nvidia-container-toolkit=${NVIDIA_CONTAINER_TOOLKIT_VERSION} \
    nvidia-container-toolkit-base=${NVIDIA_CONTAINER_TOOLKIT_VERSION} \
    libnvidia-container-tools=${NVIDIA_CONTAINER_TOOLKIT_VERSION} \
    libnvidia-container1=${NVIDIA_CONTAINER_TOOLKIT_VERSION}

# CDI spec management: nvidia-cdi-refresh (shipped in toolkit-base 1.20.x)
# regenerates the spec as root to /var/run/cdi/nvidia.yaml - at boot AND on
# driver/toolkit changes (the .path unit watches modules.dep + nvidia-ctk).
# /var/run/cdi is a DEFAULT cdi search path for every user, so the rootless
# podman user picks it up with zero config: no containers.conf edit and no
# user-level spec copy needed.
sudo systemctl enable --now nvidia-cdi-refresh.path
sudo systemctl enable --now nvidia-cdi-refresh.service
 
