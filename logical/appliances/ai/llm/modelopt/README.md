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

### nvfp4 + fp8 kv cache - dataset optimized for reasoning
CUDA_DEVICE_ORDER=PCI_BUS_ID \
CUDA_VISIBLE_DEVICES=1,0 \
PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True \
python hf_ptq.py \
 --pyt_ckpt_path /models/gemma4/google-gemma-4-31B-it \
 --qformat nvfp4_mse \
 --kv_cache_qformat fp8 \
 --dataset allenai/tulu-3-sft-mixture \
 --calib_size 512 \
 --calib_seq 512 \
 --batch_size 1 \
 --export_path /models/gemma4/google-gemma-4-31b-it-nvfp4mse-tulu3sftmixture \
 --trust_remote_code \
 --use_seq_device_map \
 --gpu_max_mem_percentage 0.70 \
 --skip_generate

### make text-only

python3 make-gemma4-text-only.py \
 /models/gemma4/google-gemma-4-31b-it-nvfp4 \
 /models/gemma4/google-gemma-4-31b-it-nvfp4-text-only

python3 make-gemma4-text-only.py \
 /models/gemma4/google-gemma-4-31b-it-nvfp4mse-tulu3sftmixture \
 /models/gemma4/google-gemma-4-31b-it-nvfp4mse-tulu3sftmixture-text-only

### nvfp4 + fp4 kv cache

python hf_ptq.py \
 --pyt_ckpt_path /models/gemma4/google-gemma-4-31B-it \
 --qformat nvfp4_mse \
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

### huggingface
https://huggingface.co/AEON-7/Gemma-4-31B-it-DECKARD-HERETIC-Uncensored-NVFP4-SVDQuant

https://huggingface.co/AEON-7/Gemma-4-31B-it-DECKARD-HERETIC-Uncensored-NVFP4

https://huggingface.co/ManniX-ITA/Gemma-4-31B-it-NVFP4A16


FLASHINFER_DISABLE_VERSION_CHECK=1 \
PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True \
CUDA_DEVICE_ORDER=PCI_BUS_ID CUDA_VISIBLE_DEVICES=1 \
vllm serve /models/gemma4/AEON-7-Gemma-4-31B-it-DECKARD-HERETIC-Uncensored-NVFP4-SVDQuant \
  --quantization modelopt_fp4 \
  --kv-cache-dtype fp8 \
  --kv-offloading-size 8 \
  --gpu-memory-utilization 0.95 \
  --max-num-seqs 2 \
  --max-model-len 65536 \
  --max-num-batched-tokens 8192 \
  --async-scheduling \
  --load-format instanttensor \
  --enable-prefix-caching \
  --enable-chunked-prefill \
  --enable-auto-tool-choice \
  --tool-call-parser gemma4 \
  --reasoning-parser gemma4 \
  --language-model-only \
  --no-disable-cascade-attn \
  --performance-mode interactivity \
  --default-chat-template-kwargs '{"enable_thinking": false, "thinking_budget": 8192}' \
  --chat-template /root/workspace/vllm/vllm/examples/tool_chat_template_gemma4.jinja \
  --speculative-config '{"num_speculative_tokens": 4, "method": "mtp", "model":"/models/gemma4/google-gemma-4-31B-it-assistant"}' \
  --served-model-name Gemma4-31b-it \
  --port 8000 \
  --host 0.0.0.0