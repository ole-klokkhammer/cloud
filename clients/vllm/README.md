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


-- ui
https://docs.vllm.ai/en/latest/deployment/frameworks/open-webui/

docker run -d \
    --name open-webui \
    -p 3000:8080 \
    -v open-webui:/app/backend/data \
    -e OPENAI_API_BASE_URL=http://gpu-worker-0:8000/v1 \
    --restart always \
    ghcr.io/open-webui/open-webui:main