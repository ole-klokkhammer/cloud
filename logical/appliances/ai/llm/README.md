# GPU worker

## storage
sudo zfs create -o compression=lz4 -o atime=off ssd/llm/models
sudo zfs set logbias=latency ssd/llm/models
sudo zfs set recordsize=1M  ssd/llm/models 

## setup
- lxc profile create llm
- lxc profile edit llm
- lxc launch ubuntu:24.04 llm -p default -p llm
- lxc exec llm -- bash

### vllm setup
https://docs.vllm.ai/en/latest/getting_started/quickstart/


#### install uv
https://docs.astral.sh/uv/

curl -LsSf https://astral.sh/uv/install.sh | sh

#### install 
uv venv --python 3.12 --seed
source .venv/bin/activate
uv pip install vllm --torch-backend=auto