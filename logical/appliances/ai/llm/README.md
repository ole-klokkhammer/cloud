# GPU worker

## storage
sudo zfs create -o compression=lz4 -o atime=off ssd/llm/models
sudo zfs set logbias=latency ssd/llm/models
sudo zfs set recordsize=1M  ssd/llm/models 

## setup
lxc profile create llm
lxc profile edit llm
lxc launch ubuntu:24.04 llm -p default -p llm
lxc exec llm -- bash

### vllm setup
https://docs.vllm.ai/en/latest/getting_started/quickstart/


#### install uv
https://docs.astral.sh/uv/

curl -LsSf https://astral.sh/uv/install.sh | sh

#### install vllm
wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2404/x86_64/cuda-keyring_1.1-1_all.deb
sudo dpkg -i cuda-keyring_1.1-1_all.deb
sudo apt-get update
sudo apt-get -y install cuda-toolkit-13-3 gcc build-essential python3.12-dev wget ninja-build

uv venv --python 3.12 --seed --managed-python
source .venv/bin/activate
uv pip install vllm --torch-backend=auto
uv pip install instanttensor

--> optional
uv pip install flashinfer-python flashinfer-cubin
uv pip install flashinfer-jit-cache --index-url https://flashinfer.ai/whl/cu132
flashinfer show-config


## notes on quantized assistant model
https://huggingface.co/melcheikh/gemma-4-31B-it-qat-assistant-NVFP4-Blackwell

enable quant_config