https://docs.vllm.ai/en/latest/getting_started/installation/gpu/

## setup
uv venv --python 3.12 --seed
source .venv/bin/activate

uv pip install vllm --torch-backend=auto

flashinfer
https://docs.flashinfer.ai/installation.html

uv pip install flashinfer-python
uv pip install flashinfer-python flashinfer-cubin
uv pip install flashinfer-jit-cache --index-url https://flashinfer.ai/whl/cu130
flashinfer show-config

-- upgrade
uv pip install -U vllm --torch-backend=auto

-- example
hf download llmat/Qwen3-4B-Instruct-2507-NVFP4 --local-dir /models/Qwen3-4B-Instruct-2507-NVFP4


-- ui
https://docs.vllm.ai/en/latest/deployment/frameworks/open-webui/

docker run -d \
    --network=host \
    --name open-webui \
    -v open-webui:/app/backend/data \
    -e OPENAI_API_BASE_URL=http://0.0.0.0:8000/v1 \
    --restart always \
    ghcr.io/open-webui/open-webui:main

### upgrade
pip install vllm --pre --upgrade

## models

### minimax m2.1
https://huggingface.co/QuantTrio/MiniMax-M2.1-AWQ


export VLLM_USE_DEEP_GEMM=0
export VLLM_USE_FLASHINFER_MOE_FP16=1
export VLLM_USE_FLASHINFER_SAMPLER=0
export OMP_NUM_THREADS=4

vllm serve \
    --model /models/minimax-m2.1/QuantTrio/MiniMax-M2.1-AWQ \
    --served-model-name MiniMax-M2.1-AWQ \
    --swap-space 16 \
    --max-num-seqs 4 \
    --max-model-len 32768  \
    --cpu-offload-gb 200 \
    --gpu-memory-utilization 0.9 \
    --tensor-parallel-size 1 \
    --enable-auto-tool-choice \
    --tool-call-parser minimax_m2 \
    --reasoning-parser minimax_m2_append_think \
    --trust-remote-code \
    --host 0.0.0.0 \
    --port 8000

### nemotron 3 nano
export VLLM_USE_V1=1
export VLLM_USE_FLASHINFER_MOE_FP4=1
export VLLM_FLASHINFER_MOE_BACKEND=throughput
export VLLM_ATTENTION_BACKEND=FLASHINFER 
export CUDA_COMPUTE_CAPABILITY=120
export VLLM_CUDA_GRAPH_MODE=full_and_piecewise 


vllm serve /models/nemotron3-nano-nvfp4/nemotron3-nano-nvfp4-w4a16 \
  --served-model-name nemotron3-nano-nvfp4-w4a16 \
  --trust-remote-code \
  --attention-config.backend FLASHINFER \
  --quantization modelopt_fp4 \
  --cpu-offload-gb 20 \
  --gpu-memory-utilization 0.5 \
  --max-model-len 1024 \
  --max-num-seqs 1 \
  --kv-cache-dtype fp8 \
  --enforce-eager \
  --host 0.0.0.0 --port 8000


# qwen3 coder next
The version check is just a safety guard — the APIs between 0.6.1 and 0.6.4 are compatible.

export FLASHINFER_DISABLE_VERSION_CHECK=1
export CUDA_DEVICE_ORDER=PCI_BUS_ID
export CUDA_VISIBLE_DEVICES=0,1

vllm serve Qwen/Qwen3-Coder-30B-A3B-Instruct-FP8 \
    --max-model-len 32768 \
    --kv-cache-dtype fp8 \
    --pipeline-parallel-size 2 \
    --gpu-memory-utilization 0.9 \
    --host 0.0.0.0 --port 8000 


## Qwen3-Coder-30B-A3B-Instruct 
export FLASHINFER_DISABLE_VERSION_CHECK=1
export CUDA_DEVICE_ORDER=PCI_BUS_ID
export CUDA_VISIBLE_DEVICES=1

vllm serve /models/Qwen3.5-27B \
  --served-model-name Qwen3.5-27B \
  --max-model-len 8096 \
  --enforce-eager \
  --host 0.0.0.0 --port 8000
 

# recommended sampling params (set in API request body, not CLI):
# temperature=0.7, top_p=0.8, top_k=20, repetition_penalty=1.05

vllm serve /models/Qwen3.5-27B-NVFP4 \
  --served-model-name Qwen3.5-27B \
  --quantization modelopt_fp4 \
  --max-model-len 16384 \
  --enforce-eager \
  --host 0.0.0.0 --port 8000


Kbenkhaled/Qwen3.5-27B-NVFP4
Kbenkhaled/Qwen3.5-35B-A3B-NVFP4
 

## gemma 4 - speculative decoding
export CUDA_DEVICE_ORDER=PCI_BUS_ID
export CUDA_VISIBLE_DEVICES=1

VLLM_ATTENTION_BACKEND=FLASHINFER vllm serve /models/gemma4/redhatai-31b-it-nvfp4 \
  --served-model-name gemma-4-31b-nvfp4 \
  --tensor-parallel-size 1 \
  --reasoning-parser gemma4 \
  --tool-call-parser gemma4 \
  --limit-mm-per-prompt '{"image": 0, "video": 0}' \
  --max-model-len 16384 \
  --kv-cache-dtype fp8 \
  --kv-cache-memory 9275048960 \
  --enable-auto-tool-choice \
  --trust-remote-code \
  --host 0.0.0.0 --port 8000


NotImplementedError: Speculative Decoding with draft models or parallel drafting does not support multimodal models yet


    --speculative-config '{
    "method": "draft_model",
    "model": "/models/gemma4/google-e2b-it",
    "num_speculative_tokens": 5,
    "draft_tensor_parallel_size": 1,
    "quantization": "fp8"
  }' \

### test
curl http://core-gpu.home.lan:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gemma-4-31b-nvfp4",
    "messages": [{"role": "user", "content": "Hello, what model are you?"}],
    "max_tokens": 256
  }'

curl http://core-gpu.home.lan:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gemma-4-31b-nvfp4",
    "messages": [{"role": "user", "content": "Write a haiku about coding"}],
    "max_tokens": 256,
    "stream": true
  }'