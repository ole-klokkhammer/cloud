# fp4-hybrid
model quantizing

## setup
cd ~/workspace
git clone https://github.com/NVIDIA/Model-Optimizer.git
cd Model-Optimizer/examples/llm_ptq

uv venv .venv
source .venv/bin/activate

uv pip install -U pip setuptools wheel ninja packaging
uv pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu128
uv pip install flash-attn==2.8.3 --no-build-isolation
uv pip install -U nvidia-modelopt[hf]
uv pip install -r requirements.txt --no-build-isolation

## export 

### nvfp4 + fp8 kv cache
python hf_ptq.py \
  --pyt_ckpt_path /models/gemma4/google-gemma-4-31B-it \
  --qformat nvfp4 \
  --kv_cache_qformat fp8_cast \
  --dataset cnn_dailymail \
  --calib_size 128 \
  --calib_seq 512 \
  --batch_size 1 \
  --export_path /models/gemma4/google-gemma-4-31b-it-nvfp4 \
  --trust_remote_code \
  --use_seq_device_map \
  --skip_generate

du -sh /models/gemma4/google-gemma-4-31b-it-nvfp4

FLASHINFER_DISABLE_VERSION_CHECK=1 \
PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True \
CUDA_DEVICE_ORDER=PCI_BUS_ID CUDA_VISIBLE_DEVICES=1 vllm serve /models/gemma4/google-gemma-4-31b-it-nvfp4 \
  --quantization modelopt_fp4 \
  --kv-cache-dtype fp8_e4m3 \
  --gpu-memory-utilization 0.98 \
  --max-num-seqs 1 \
  --max-model-len 32000 \
  --max-num-batched-tokens 8192 \
  --served-model-name Gemma4-31b-it \
  --port 8000 \
  --host 0.0.0.0 \
  --async-scheduling \
  --load-format instanttensor \
  --enable-prefix-caching \
  --enable-chunked-prefill \
  --enable-auto-tool-choice \
  --tool-call-parser gemma4 \
  --reasoning-parser gemma4 \
  --default-chat-template-kwargs '{"enable_thinking": true}' \
  --chat-template ./vllm/examples/tool_chat_template_gemma4.jinja \
  --speculative-config '{"num_speculative_tokens": 4, "method": "mtp", "model":"/models/gemma4/google-gemma-4-31B-it-assistant"}'

### make text-only
python3 make-gemma4-text-only.py \
  /models/gemma4/google-gemma-4-31b-it-nvfp4 \
  /models/gemma4/google-gemma-4-31b-it-nvfp4-text-only

FLASHINFER_DISABLE_VERSION_CHECK=1 \
CUDA_DEVICE_ORDER=PCI_BUS_ID CUDA_VISIBLE_DEVICES=1 vllm serve /models/gemma4/google-gemma-4-31b-it-nvfp4-text-only \
  --quantization modelopt_fp4 \
  --kv-cache-dtype fp8_e4m3 \
  --kv-offloading-size 4 \
  --gpu-memory-utilization 0.98 \
  --max-num-seqs 1 \
  --max-model-len 64000 \
  --max-num-batched-tokens 8192 \
  --served-model-name Gemma4-31b-it \
  --port 8000 \
  --host 0.0.0.0 \
  --async-scheduling \
  --load-format instanttensor \
  --enable-prefix-caching \
  --enable-chunked-prefill \
  --enable-auto-tool-choice \
  --tool-call-parser gemma4 \
  --reasoning-parser gemma4 \
  --default-chat-template-kwargs '{"enable_thinking": true}' \
  --chat-template ./vllm/examples/tool_chat_template_gemma4.jinja \
  --speculative-config '{"num_speculative_tokens": 4, "method": "mtp", "model":"/models/gemma4/google-gemma-4-31B-it-assistant"}'

 

### nvfp4 + fp4 kv cache
python hf_ptq.py \
  --pyt_ckpt_path /models/gemma4/google-gemma-4-31B-it \
  --qformat nvfp4 \
  --kv_cache_qformat nvfp4_cast \
  --dataset cnn_dailymail \
  --calib_size 128 \
  --calib_seq 512 \
  --batch_size 1 \
  --export_path /models/gemma4/google-gemma-4-31b-it-nvfp4-kv-fp4 \
  --trust_remote_code \
  --use_seq_device_map \
  --skip_generate

du -sh /models/gemma4/google-gemma-4-31b-it-nvfp4-kv-fp4


FLASHINFER_DISABLE_VERSION_CHECK=1 \
PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True \
CUDA_DEVICE_ORDER=PCI_BUS_ID CUDA_VISIBLE_DEVICES=1 vllm serve /models/gemma4/google-gemma-4-31b-it-nvfp4-kv-fp4 \
  --quantization modelopt_fp4 \
  --kv-cache-dtype auto \
  --gpu-memory-utilization 0.98 \
  --max-num-seqs 1 \
  --max-model-len 32000 \
  --max-num-batched-tokens 8192 \
  --served-model-name Gemma4-31b-it \
  --port 8000 \
  --host 0.0.0.0 \
  --async-scheduling \
  --load-format instanttensor \
  --enable-prefix-caching \
  --enable-chunked-prefill \
  --enable-auto-tool-choice \
  --tool-call-parser gemma4 \
  --reasoning-parser gemma4 \
  --default-chat-template-kwargs '{"enable_thinking": true}' \
  --chat-template ./vllm/examples/tool_chat_template_gemma4.jinja \
  --limit-mm-per-prompt '{"image": 0, "audio": 0, "video": 0}' \
  --speculative-config '{"num_speculative_tokens": 4, "method": "mtp", "model":"/models/gemma4/google-gemma-4-31B-it-assistant"}'


#### turboquant
# vLLM 0.21.0 rejects TurboQuant for this Gemma 4 text-only checkpoint with:
# - kv_cache_dtype not supported
# - partial multimodal token full attention not supported
#
# So this is currently a negative test, not a working serve path.
# Keep using fp8_e4m3 KV cache for Gemma 4 on vLLM unless upstream support changes.
FLASHINFER_DISABLE_VERSION_CHECK=1 \
PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True \
CUDA_DEVICE_ORDER=PCI_BUS_ID CUDA_VISIBLE_DEVICES=1 \
vllm serve /models/gemma4/google-gemma-4-31b-it-nvfp4-text-only \
  --quantization modelopt_fp4 \
  --load-format instanttensor \
  --attention-backend TURBOQUANT \
  --gpu-memory-utilization 0.98 \
  --max-num-seqs 1 \
  --max-model-len 16384 \
  --max-num-batched-tokens 4096 \
  --served-model-name Gemma4-31b-it-tq \
  --port 8000 \
  --host 0.0.0.0 \
  --enable-prefix-caching \
  --enable-chunked-prefill \
  --enable-auto-tool-choice \
  --tool-call-parser gemma4 \
  --reasoning-parser gemma4 \
  --default-chat-template-kwargs '{"enable_thinking": true}' \
  --chat-template ./vllm/examples/tool_chat_template_gemma4.jinja

# Fallback working path for Gemma 4:
# use the fp8_e4m3 command above instead of TurboQuant.