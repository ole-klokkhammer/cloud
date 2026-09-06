# Opennvr

## setup
https://opennvr.org/

### disk

sudo zfs create -o compression=lz4 -o atime=off -o xattr=sa -o acltype=posixacl -o recordsize=1M ssd/appdata/opennvr

### lxc

lxc profile create opennvr
lxc profile edit opennvr
lxc launch ubuntu:24.04 opennvr -p default -p opennvr
lxc exec opennvr -- bash

#### install podman

https://podman.io/docs/installation

sudo apt update && sudo apt install -y podman systemd-container 

enable auto update
systemctl enable --now podman-auto-update.timer
systemctl list-timers | grep podman-auto-update


sudo ln -s "$(command -v podman)" /usr/local/bin/docker


#### nvidia container toolkit
sudo apt-get update && sudo apt-get install -y --no-install-recommends \
   ca-certificates \
   curl \
   gnupg2
  
curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg \
  && curl -s -L https://nvidia.github.io/libnvidia-container/stable/deb/nvidia-container-toolkit.list | \
    sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' | \
    sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list

sudo apt-get update

export NVIDIA_CONTAINER_TOOLKIT_VERSION=1.20.0-1
  sudo apt-get install -y \
      nvidia-container-toolkit=${NVIDIA_CONTAINER_TOOLKIT_VERSION} \
      nvidia-container-toolkit-base=${NVIDIA_CONTAINER_TOOLKIT_VERSION} \
      libnvidia-container-tools=${NVIDIA_CONTAINER_TOOLKIT_VERSION} \
      libnvidia-container1=${NVIDIA_CONTAINER_TOOLKIT_VERSION}

sudo nvidia-ctk cdi generate --output=/etc/cdi/

#### Fix DNS
  raw.lxc: |
    lxc.apparmor.profile = unconfined
    lxc.cap.drop =
  security.nesting: "true"

#### detector model
https://docs.frigate.video/configuration/object_detectors/#onnx-supported-models

podman build . --build-arg MODEL_SIZE=Medium --rm --output . -f- <<'EOF'
FROM python:3.12 AS build
RUN apt-get update && apt-get install --no-install-recommends -y libgl1 && rm -rf /var/lib/apt/lists/*
COPY --from=ghcr.io/astral-sh/uv:0.10.4 /uv /bin/
WORKDIR /rfdetr
RUN uv pip install --system rfdetr[onnxexport] torch==2.8.0 onnx==1.19.1 transformers==4.57.6 onnxscript
ARG MODEL_SIZE
RUN python3 -c "from rfdetr import RFDETR${MODEL_SIZE}; x = RFDETR${MODEL_SIZE}(resolution=320); x.export(simplify=True)"
FROM scratch
ARG MODEL_SIZE
COPY --from=build /rfdetr/output/inference_model.onnx /rfdetr-${MODEL_SIZE}.onnx
EOF