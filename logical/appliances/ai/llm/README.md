# GPU worker

## storage

sudo zfs create -o compression=lz4 -o atime=off ssd/llm/models
sudo zfs set logbias=latency ssd/llm/models
sudo zfs set recordsize=1M ssd/llm/models

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
sudo apt-get -y install cuda-toolkit-13-3 gcc build-essential python3.12-dev wget ninja-build ffmpeg

uv venv --python 3.12 --seed --managed-python
source .venv/bin/activate
uv pip install vllm --torch-backend=auto
uv pip install instanttensor
uv pip uninstall torchaudio

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

## blackwell mtp

hf download melcheikh/gemma-4-31B-it-qat-assistant-NVFP4-mse-Blackwell --local-dir /models/gemma4/melcheikh_gemma-4-31B-it-qat-assistant-NVFP4-mse-Blackwell
hf download google/gemma-4-31B-it-qat-q4_0-unquantized-assistant --local-dir /models/gemma4/google_gemma-4-31B-it-qat-q4_0-unquantized-assistant


## CLEAN CACHE if hEEEEELP
rm -rf ~/.triton/cache
rm -rf ~/.cache/huggingface/modules/
uv cache clean

### MAYBE USE PODMAN

sudo apt update && sudo apt install podman

curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg \
  && curl -s -L https://nvidia.github.io/libnvidia-container/stable/deb/nvidia-container-toolkit.list | \
    sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' | \
    sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list
sudo apt-get update
export NVIDIA_CONTAINER_TOOLKIT_VERSION=1.17.8-1
sudo apt-get install -y \
      nvidia-container-toolkit=${NVIDIA_CONTAINER_TOOLKIT_VERSION} \
      nvidia-container-toolkit-base=${NVIDIA_CONTAINER_TOOLKIT_VERSION} \
      libnvidia-container-tools=${NVIDIA_CONTAINER_TOOLKIT_VERSION} \
      libnvidia-container1=${NVIDIA_CONTAINER_TOOLKIT_VERSION}
sudo nvidia-ctk runtime configure --runtime=containerd 

podman run --gpus all \
  -p 8000:8000 \
  --ipc=host \
  docker.io/vllm/vllm-openai:v0.25.1 \
    --model /models/gemma4/google-gemma-4-31b-it-abliterated-nvfp4mse \
    --quantization modelopt_fp4 \
    --kv-cache-dtype fp8_e4m3 \
    --kv-offloading-size 32 \
    --gpu-memory-utilization 0.90 \
    --max-num-seqs 32 \
    --max-model-len 65536 \
    --max-num-batched-tokens 8192 \
    --load-format instanttensor \
    --enable-chunked-prefill \
    --enable-prefix-caching \
    --enable-auto-tool-choice \
    --tool-call-parser gemma4 \
    --reasoning-parser gemma4 \
    --language-model-only \
    --performance-mode interactivity \
    --default-chat-template-kwargs '{"enable_thinking": false, "thinking_budget": 8192}' \
    --chat-template /models/TEMPLATES/tool_chat_template_gemma4_v2.jinja \
    --speculative-config '{"num_speculative_tokens": 4, "method": "mtp", "model":"/models/gemma4/google-gemma-4-31B-it-assistant"}' \
    --served-model-name Gemma4-31b-it \
    --port 8000 \
    --host 0.0.0.0