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

## 0.24 error
https://github.com/vllm-project/vllm/pull/45544/commits

## notes on quantized assistant model
https://huggingface.co/melcheikh/gemma-4-31B-it-qat-assistant-NVFP4-Blackwell

enable quant_config

## 0.25
sudo apt-get update
sudo apt-get install -y ffmpeg libavcodec-dev libavformat-dev libavutil-dev

## creating text only and abliteration
https://huggingface.co/wangzhang/gemma-4-31B-it-abliterated

then strip it for text only

and run i.e.: 
python3 make-gemma4-text-only.py \
  /models/gemma4/wangzhang-gemma-4-31B-it-abliterated \
  /models/gemma4/wangzhang-gemma-4-31B-it-abliterated-text-only


CUDA_DEVICE_ORDER=PCI_BUS_ID \
CUDA_VISIBLE_DEVICES=1 \
PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True \
python ./examples/llm_ptq/hf_ptq.py \
 --pyt_ckpt_path /models/gemma4/wangzhang-gemma-4-31B-it-abliterated-text-only \
 --qformat nvfp4_mse \
 --kv_cache_qformat fp8 \
 --calib_size 512 \
 --calib_seq 2048 \
 --batch_size 1 \
 --dataset allenai/tulu-3-sft-mixture \
 --export_path /models/gemma4/google-gemma-4-31b-it-abliterated-nvfp4mse \
 --trust_remote_code \
 --gpu_max_mem_percentage 0.50 \
 --skip_generate

## updates to gemma4
update tokenizer_config.json to newest based on [google](https://huggingface.co/google/gemma-4-31B-it/tree/main) 
