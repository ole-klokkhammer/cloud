# vllm

https://docs.vllm.ai/en/latest/getting_started/installation/gpu/

## setup
uv venv --python 3.12 --seed
source .venv/bin/activate

uv pip install vllm --torch-backend=auto

-- example
hf download llmat/Qwen3-4B-Instruct-2507-NVFP4 --local-dir /models/Qwen3-4B-Instruct-2507-NVFP4

-- set  max_model_len to no more than available space left on vram
vllm serve \
    --model /models/Qwen3-4B-Instruct-2507-NVFP4 \
    --served-model-name Qwen3-4B-Instruct-2507-NVFP4 \
    --reasoning-parser deepseek_r1 \
    --enable-auto-tool-choice \
    --tool-call-parser hermes \
    --max_model_len 58254 \
    --dtype float16 \
    --host 0.0.0.0 \
    --port 8000

-- offloading
VLLM_USE_V1=1 \
VLLM_ATTENTION_BACKEND=FLASHINFER \
VLLM_CUDA_GRAPH_MODE=full_and_piecewise \
VLLM_USE_FLASHINFER_MOE_FP4=1 \
VLLM_FLASHINFER_MOE_BACKEND=throughput \
vllm serve \
  --model /models/nemotron3-nano-nvfp4/nemotron3-nano-nvfp4-w4a16 \
  --served-model-name nemotron3-nano-nvfp4-w4a16 \
  --trust-remote-code \
  --max-model-len 1024 \
  --cpu_offload_gb 64 \
  --gpu-memory-utilization 0.95
  --quantization modelopt_fp4 \
  --kv-cache-dtype fp8 \
  --enforce-eager \
  --host 0.0.0.0 \
  --port 8000

-- ui
https://docs.vllm.ai/en/latest/deployment/frameworks/open-webui/

docker run -d \
    --name open-webui \
    -p 3000:8080 \
    -v open-webui:/app/backend/data \
    -e OPENAI_API_BASE_URL=http://gpu-worker-0:8000/v1 \
    --restart always \
    ghcr.io/open-webui/open-webui:main