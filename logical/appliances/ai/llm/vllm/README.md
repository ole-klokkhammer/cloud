https://docs.vllm.ai/en/latest/getting_started/installation/gpu/

## setup
sudo apt update
snap install astral-uv

uv venv --python 3.12 --seed
source .venv/bin/activate

uv pip install vllm --torch-backend=auto

flashinfer
https://docs.flashinfer.ai/installation.html

uv pip install flashinfer-python flashinfer-cubin
uv pip install flashinfer-jit-cache --index-url https://flashinfer.ai/whl/cu132
flashinfer show-config

uv pip install instanttensor

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

### polarengine
https://github.com/caiovicentino/polarengine-vllm

### turboquant
uv pip install turboquant-vllm 
https://pypi.org/project/turboquant-vllm/

  Plugin path:
  - use `--attention-backend CUSTOM`
  - optionally set `TQ4_K_BITS` and `TQ4_V_BITS`
  - do not combine this with `--kv-cache-dtype turboquant_*`

  Built-in vLLM path:
  - use `--attention-backend TURBOQUANT`
  - pair it with a specific `--kv-cache-dtype` such as `turboquant_4bit_nc`
  - do not use `TQ4_K_BITS` or `TQ4_V_BITS` with this path

  If vLLM says `Selected backend AttentionBackendEnum.CUSTOM is not valid for this configuration. Reason: ['kv_cache_dtype not supported']`, remove `--kv-cache-dtype turboquant_*` from the CUSTOM/plugin command or switch the backend to `TURBOQUANT`.

### upgrade
uv pip install -U vllm --torch-backend=auto --extra-index-url https://wheels.vllm.ai/nightly/cu132

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

## plain
FLASHINFER_DISABLE_VERSION_CHECK=1 \
TQ4_K_BITS=4 TQ4_V_BITS=3 \
PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True \
CUDA_DEVICE_ORDER=PCI_BUS_ID CUDA_VISIBLE_DEVICES=1 vllm serve /models/gemma4/nvidia-31b-it-nvfp4 \
  --tensor-parallel-size 1 \
  --reasoning-parser gemma4 \
  --tool-call-parser gemma4 \
  --limit-mm-per-prompt '{"image": 0, "video": 0}' \
  --max-model-len 16384 \
  --attention-backend TURBOQUANT \
  --kv-cache-dtype turboquant_4bit_nc \
  --kv-cache-memory 9275048960 \
  --enable-auto-tool-choice \
  --trust-remote-code \
  --host 0.0.0.0 --port 8000

## https://huggingface.co/caiovicentino1/Gemma-4-31B-it-HLWQ-Q5-Vision
hf download caiovicentino1/Gemma-4-31B-it-HLWQ-Q5-Vision --local-dir /models/gemma4/caiovicentino1-Gemma-4-31B-it-HLWQ-Q5-Vision
uv pip install https://github.com/caiovicentino/polarengine-vllm.git


FLASHINFER_DISABLE_VERSION_CHECK=1 \
PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True \
CUDA_DEVICE_ORDER=PCI_BUS_ID CUDA_VISIBLE_DEVICES=1 vllm serve /models/gemma4/caiovicentino1-Gemma-4-31B-it-HLWQ-Q5-Vision \
  --tensor-parallel-size 1 \
  --reasoning-parser gemma4 \
  --tool-call-parser gemma4 \
  --max-model-len 8192 \
  --max-num-batched-tokens 4096 \
  --max-num-seqs 1 \
  --kv-cache-dtype fp8 \
  --enforce-eager \
  --enable-auto-tool-choice \
  --trust-remote-code \
  --host 0.0.0.0 --port 8000

## https://huggingface.co/LilaRest/gemma-4-31B-it-NVFP4-turbo
FLASHINFER_DISABLE_VERSION_CHECK=1 \
PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True \
CUDA_DEVICE_ORDER=PCI_BUS_ID CUDA_VISIBLE_DEVICES=1 vllm serve LilaRest/gemma-4-31B-it-NVFP4-turbo \
  --quantization modelopt \
  --reasoning-parser gemma4 \
  --tool-call-parser gemma4 \
  --enable-auto-tool-choice \
  --default-chat-template-kwargs '{"enable_thinking": true}' \
  --max-model-len 64000 \
  --max-num-seqs 128 \
  --max-num-batched-tokens 8192 \
  --gpu-memory-utilization 0.95 \
  --kv-cache-dtype fp8 \
  --enable-prefix-caching \
  --trust-remote-code \
  --host 0.0.0.0 --port 8000

## https://huggingface.co/redhat
FLASHINFER_DISABLE_VERSION_CHECK=1 \
PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True \
CUDA_DEVICE_ORDER=PCI_BUS_ID CUDA_VISIBLE_DEVICES=1 vllm serve /models/gemma4/redhat \
  --quantization modelopt \
  --max-model-len 32000 \
  --max-num-seqs 128 \
  --max-num-batched-tokens 8192 \
  --gpu-memory-utilization 0.95 \
  --kv-cache-dtype fp8 \
  --enable-prefix-caching \
  --trust-remote-code \
  --host 0.0.0.0 --port 8000

# https://huggingface.co/thetom-ai/Gemma-4-31B-it-TQPlus


## gemma4 mtp 

https://forums.developer.nvidia.com/t/has-anyone-actually-succeeded-in-deploying-gemma4-dense-using-both-the-new-mtp-and-turboquant/369248/2

https://dasroot.net/posts/2026/05/gemma-4-speed-hacks-mtp-dflash-local-inference/

https://docs.vllm.ai/projects/recipes/en/latest/Google/Gemma4.html#amd-gpu-deployment-mi300x-mi325x-mi350x-mi355x-via-docker

### https://huggingface.co/ebircak/gemma-4-31B-it-4bit-NVFP4A16-GPTQ

FLASHINFER_DISABLE_VERSION_CHECK=1 \
PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True \
CUDA_DEVICE_ORDER=PCI_BUS_ID CUDA_VISIBLE_DEVICES=1 vllm serve LilaRest/gemma-4-31B-it-NVFP4-turbo  \
  --served-model-name Gemma4-31b-it \
  --port 8000 \
  --host 0.0.0.0 \
  --cpu-offload-gb 10 \
  --gpu-memory-utilization 0.98 \
  --max-model-len 64000 \
  --max-num-batched-tokens 16384 \
  --kv-cache-dtype fp8 \
  --quantization compressed-tensors \
  --load-format instanttensor \
  --async-scheduling \
  --enable-prefix-caching \
  --enable-chunked-prefill \
  --enable-auto-tool-choice \
  --tool-call-parser gemma4 \
  --reasoning-parser gemma4 \
  --chat-template ./vllm/examples/tool_chat_template_gemma4.jinja \
  --limit-mm-per-prompt '{"image": 0, "audio": 0, "video": 0}' \
  --default-chat-template-kwargs '{"enable_thinking": true}' \
  --speculative-config '{"num_speculative_tokens": 4, "method": "mtp", "model":"/models/gemma4/google-gemma-4-31B-it-assistant"}'

add when merged into vllm: heuristics: true
also consider switching to redhat for more consistent quantization scales
maybe we can add this then: --calculate_kv_scales \

### redhatai
FLASHINFER_DISABLE_VERSION_CHECK=1 \
PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True \
CUDA_DEVICE_ORDER=PCI_BUS_ID CUDA_VISIBLE_DEVICES=1 vllm serve LilaRest/gemma-4-31B-it-NVFP4-turbo \
  --served-model-name Gemma4-31b-it \
  --port 8000 \
  --host 0.0.0.0 \
  --max-num-seqs 1 \
  --gpu-memory-utilization 0.98 \
  --max-model-len 64000 \
  --max-num-batched-tokens 8192 \
  --kv-cache-dtype fp8 \
  --quantization modelopt \
  --load-format instanttensor \
  --async-scheduling \
  --enable-prefix-caching \
  --enable-chunked-prefill \
  --enable-auto-tool-choice \
  --tool-call-parser gemma4 \
  --reasoning-parser gemma4 \
  --chat-template ./vllm/examples/tool_chat_template_gemma4.jinja \
  --limit-mm-per-prompt '{"image": 0, "audio": 0, "video": 0}' \
  --default-chat-template-kwargs '{"enable_thinking": true}' \
  --speculative-config '{"num_speculative_tokens": 4, "method": "mtp", "model":"/models/gemma4/google-gemma-4-31B-it-assistant"}'


FLASHINFER_DISABLE_VERSION_CHECK=1 \
PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True \
CUDA_DEVICE_ORDER=PCI_BUS_ID CUDA_VISIBLE_DEVICES=1 vllm serve LilaRest/gemma-4-31B-it-NVFP4-turbo \
  --quantization modelopt \
  --reasoning-parser gemma4 \
  --tool-call-parser gemma4 \
  --enable-auto-tool-choice \
  --default-chat-template-kwargs '{"enable_thinking": true}' \
  --max-model-len 64000 \
  --max-num-seqs 128 \
  --max-num-batched-tokens 8192 \
  --gpu-memory-utilization 0.95 \
  --kv-cache-dtype fp8 \
  --enable-prefix-caching \
  --trust-remote-code \
  --host 0.0.0.0 --port 8000


### redhat text only
FLASHINFER_DISABLE_VERSION_CHECK=1 \
PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True \
CUDA_DEVICE_ORDER=PCI_BUS_ID CUDA_VISIBLE_DEVICES=1 vllm serve /models/gemma4/redhatai-31b-it-nvfp4-text-only \
  --quantization compressed-tensors \
  --load-format instanttensor \
  --served-model-name Gemma4-31b-it \
  --port 8000 \
  --host 0.0.0.0 \
  --gpu-memory-utilization 0.981 \
  --max-num-seqs 1 \
  --max-model-len 84000 \
  --max-num-batched-tokens 8192 \
  --kv-cache-dtype fp8 \
  --async-scheduling \
  --enable-prefix-caching \
  --enable-chunked-prefill \
  --enable-auto-tool-choice \
  --tool-call-parser gemma4 \
  --reasoning-parser gemma4 \
  --chat-template ./vllm/examples/tool_chat_template_gemma4.jinja \
  --limit-mm-per-prompt '{"image": 0, "audio": 0, "video": 0}' \
  --default-chat-template-kwargs '{"enable_thinking": true}' \
  --speculative-config '{"num_speculative_tokens": 4, "method": "mtp", "model":"/models/gemma4/google-gemma-4-31B-it-assistant"}'

### nvidia text only
FLASHINFER_DISABLE_VERSION_CHECK=1 \
PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True \
CUDA_DEVICE_ORDER=PCI_BUS_ID CUDA_VISIBLE_DEVICES=1 vllm serve /models/gemma4/nvidia-31b-it-nvfp4-text-only \
  --quantization modelopt \
  --served-model-name Gemma4-31b-it \
  --port 8000 \
  --host 0.0.0.0 \
  --gpu-memory-utilization 0.981 \
  --max-num-seqs 1 \
  --max-model-len 3000 \
  --max-num-batched-tokens 8192 \
  --kv-cache-dtype fp8 \
  --async-scheduling \
  --enable-prefix-caching \
  --enable-chunked-prefill \
  --enable-auto-tool-choice \
  --tool-call-parser gemma4 \
  --reasoning-parser gemma4 \
  --chat-template ./vllm/examples/tool_chat_template_gemma4.jinja \
  --limit-mm-per-prompt '{"image": 0, "audio": 0, "video": 0}' \
  --default-chat-template-kwargs '{"enable_thinking": true}' \
  --speculative-config '{"num_speculative_tokens": 4, "method": "mtp", "model":"/models/gemma4/google-gemma-4-31B-it-assistant"}'