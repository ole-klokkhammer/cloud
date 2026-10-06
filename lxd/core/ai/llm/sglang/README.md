#

## 
https://docs.sglang.io/cookbook/autoregressive/Qwen/Qwen3.8-27B#hw=rtx5090&variant=default&quant=nvfp4&strategy=balanced&nodes=single
https://docs.sglang.io/cookbook/autoregressive/Qwen/Qwen3.8-27B
https://docs.sglang.io/docs/references/environment_variables


sglang serve \
    --trust-remote-code \
    --model-path /models/qwen3.8/RadixArk_Qwen3.8-27B-NVFP4 \
    --kv-cache-dtype fp8_e4m3 \
    --mem-fraction-static 0.75 \
    --attention-backend flashinfer \
    --chunked-prefill-size 2048 \
    --reasoning-parser qwen3 \
    --tool-call-parser qwen3_coder \
    --mamba-ssm-dtype bfloat16 \
    --mamba-full-memory-ratio 2.34 \
    --host 0.0.0.0 \
    --port 30000
# base
export SGLANG_DEFAULT_THINKING=false
export SGLANG_MAX_THINK_TOKENS=0
sglang serve \
    --trust-remote-code \
    --model-path /models/qwen3.8/RadixArk_Qwen3.8-27B-NVFP4 \
    --attention-backend flashinfer \
    --kv-cache-dtype fp8_e4m3 \
    --mem-fraction-static 0.85 \
    --context-length 262144 \
    --chunked-prefill-size 2048 \
    --max-running-requests 2 \
    --enable-hierarchical-cache \
    --hicache-size 16 \
    --hicache-io-backend kernel \
    --mamba-ssm-dtype bfloat16 \
    --mamba-full-memory-ratio 0.9 \
    --reasoning-parser qwen3 \
    --tool-call-parser qwen3_coder \
    --host 0.0.0.0 \
    --port 8000

# mtp

sglang serve \
    --trust-remote-code \
    --model-path /models/qwen3.8/RadixArk_Qwen3.8-27B-NVFP4 \
    --mem-fraction-static 0.95 \
    --max-running-requests 1 \
    --kv-cache-dtype fp8_e4m3 \
    --attention-backend flashinfer \
    --context-length 262144 \
    --chunked-prefill-size 2048 \
    --reasoning-parser qwen3 \
    --tool-call-parser qwen3_coder \
    --speculative-algorithm EAGLE \
    --speculative-num-steps 3 \
    --speculative-eagle-topk 1 \
    --speculative-num-draft-tokens 4 \
    --mamba-ssm-dtype bfloat16 \
    --mamba-full-memory-ratio 1.2 \
    --enable-hierarchical-cache \
    --hicache-size 16 \
    --hicache-io-backend kernel \
    --host 0.0.0.0 \
    --port 8000

    
# google

sglang serve \
    --trust-remote-code \
    --model-path /models/gemma4/google-gemma-4-31b-it-abliterated-nvfp4mse \
    --mem-fraction-static 0.95 \
    --reasoning-parser gemma4 \
    --tool-call-parser gemma4 \
    --max-running-requests 1 \
    --host 0.0.0.0 \
    --port 8000