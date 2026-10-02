# sglang
https://github.com/sgl-project/sglang

## setup
https://docs.sglang.io/docs/get-started/install


### system dependencies
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
source ~/.cargo/env
sudo apt update && apt install -y protobuf-compiler ffmpeg

### python env
uv venv .venv
source .venv/bin/activate
uv pip install 'git+https://github.com/sgl-project/sglang.git#subdirectory=python'

uv pip install 'compressed-tensors==0.15.0.1' --no-deps


### possible patch?
mv /lib/x86_64-linux-gnu/libcudart.so.12 /tmp/libcudart.so.12.bak

sed -n '295,302p' /root/workspace/sglang/.venv/lib/python3.12/site-packages/sglang/srt/model_loader/weight_utils.py
sed -i 's/return quant_cls()$/return quant_cls.from_config({})/' /root/workspace/sglang/.venv/lib/python3.12/site-packages/sglang/srt/model_loader/weight_utils.py

### command
LD_PRELOAD=/usr/local/cuda/targets/x86_64-linux/lib/libcudart.so.13 \
PYTORCH_ALLOC_CONF=expandable_segments:True \
CUDA_DEVICE_ORDER=PCI_BUS_ID CUDA_VISIBLE_DEVICES=1 \
sglang serve \
    --model-path /models/gemma4/redhatai-31b-it-nvfp4 \
    --quantization compressed-tensors \
    --kv-cache-dtype fp8_e4m3 \
    --context-length 32000 \
    --enable-multimodal \
    --max-running-requests 1 \
    --reasoning-parser gemma4 \
    --tool-call-parser gemma4 \
    --trust-remote-code \
    --host 0.0.0.0 --port 30000


    

  --speculative-algorithm NEXTN \
  --speculative-draft-model-path google/gemma-4-31B-it-assistant \
  --speculative-num-steps 5 \
  --speculative-num-draft-tokens 4 \
  --speculative-eagle-topk 1 \
  --mem-fraction-static 0.981

DeepGemm is enabled but the scale_fmt of checkpoint is not ue8m0. This might cause accuracy degradation on Blackwell.
The `use_fast` parameter is deprecated and will be removed in a future version. Use `backend="torchvision"` instead of `use_fast=True`, or `backend="pil"` instead of `use_fast=False`.


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