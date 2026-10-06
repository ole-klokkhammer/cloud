podman run --device=nvidia.com/gpu=all --ipc=host -p 8000:8000 \
  -v ~/.cache/huggingface:/root/.cache/huggingface \
  -v /models:/models \
  docker.io/lmsysorg/sglang:qwen38-27b \
  sglang serve \
    --model-path /models/qwen3.8/gittensor-model-hub_Qwen3.8-27B-NVFP4-RTX5090 \
    --speculative-algorithm DSPARK \
    --speculative-draft-model-path /models/qwen3.8/gittensor-model-hub_Qwen3.8-27B-DSpark-NVFP4 \
    --speculative-draft-model-quantization modelopt_fp4 \
    --speculative-dspark-block-size 7 \
    --trust-remote-code --tp-size 1 \
    --context-length 122880 \
    --kv-cache-dtype fp8_e4m3 \
    --attention-backend flashinfer \
    --chunked-prefill-size 1024 \
    --mamba-radix-cache-strategy extra_buffer_lazy \
    --mamba-ssm-dtype bfloat16 \
    --max-mamba-cache-size 8 \
    --mm-feature-transport cpu \
    --cuda-graph-max-bs-decode 1 \
    --mem-fraction-static 0.95 \
    --max-running-requests 1 \
    --reasoning-parser qwen3 \
    --tool-call-parser qwen3_coder \
    --host 0.0.0.0 \
    --port 8000