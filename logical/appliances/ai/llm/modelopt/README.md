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
 --gpu_max_mem_percentage 0.50 \
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



### errors
(.venv) root@core-gpu:~/workspace/modelopt/Model-Optimizer/examples/llm_ptq# CUDA_DEVICE_ORDER=PCI_BUS_ID \
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
 --gpu_max_mem_percentage 0.50 \
 --skip_generate
/root/workspace/modelopt/Model-Optimizer/examples/llm_ptq/.venv/lib/python3.12/site-packages/modelopt/torch/__init__.py:53: UserWarning: transformers>=5.0 support is experimental. Unified Hugging Face checkpoint export for quantized checkpoints may not work for some models yet.
  _warnings.warn(
ModelOpt save/restore enabled for `transformers` library.
ModelOpt save/restore enabled for `diffusers` library.
ModelOpt save/restore enabled for `peft` library.
Initializing model from /models/gemma4/google-gemma-4-31B-it
`torch_dtype` is deprecated! Use `dtype` instead!
Model does not fit to the GPU mem. We apply the following memory limit for calibration: 
{0: 16568385536.0, 1: 8224866304.0, 'cpu': 127103973376}
If you hit GPU OOM issue, please adjust `gpu_mem_percentage` or reduce the calibration `batch_size` manually.
Loading weights: 100%|████████████████████████████████████████████████████████████████████████████████████████| 1188/1188 [00:03<00:00, 389.26it/s]
Some parameters are on the meta device because they were offloaded to the cpu.
Warning: Some parameters are not on a GPU. Calibration can be slow or hit OOM
Inserted 3 quantizers
Registered <class 'transformers.models.gemma4.modeling_gemma4.Gemma4VisionAttention'> to _QuantAttention for KV Cache quantization
Inserted 678 quantizers
Inserted 3 quantizers
Initializing tokenizer from /models/gemma4/google-gemma-4-31B-it
Use calib batch_size 1
Dataset 'allenai/tulu-3-sft-mixture' is not in SUPPORTED_DATASET_CONFIG. Auto-detecting format from column names.
Loading dataset with config={'path': 'allenai/tulu-3-sft-mixture'} and splits=['train']
Warning: You are sending unauthenticated requests to the HF Hub. Please set a HF_TOKEN to enable higher rate limits and faster downloads.
Enable KV cache quantization
Updated quant_cfg with KV cache quantization: {'quant_cfg': [{'quantizer_name': '*', 'enable': False}, {'quantizer_name': '*weight_quantizer', 'cfg': {'num_bits': (2, 1), 'block_sizes': {-1: 16, 'type': 'static', 'scale_bits': (4, 3)}}}, {'quantizer_name': '*input_quantizer', 'cfg': {'num_bits': (2, 1), 'block_sizes': {-1: 16, 'type': 'dynamic', 'scale_bits': (4, 3)}}}, {'parent_class': 'nn.BatchNorm1d', 'quantizer_name': '*', 'enable': False}, {'parent_class': 'nn.BatchNorm2d', 'quantizer_name': '*', 'enable': False}, {'parent_class': 'nn.BatchNorm3d', 'quantizer_name': '*', 'enable': False}, {'parent_class': 'nn.LeakyReLU', 'quantizer_name': '*', 'enable': False}, {'quantizer_name': '*lm_head*', 'enable': False}, {'quantizer_name': '*proj_out.*', 'enable': False}, {'quantizer_name': '*block_sparse_moe.gate*', 'enable': False}, {'quantizer_name': '*router*', 'enable': False}, {'quantizer_name': '*mlp.gate.*', 'enable': False}, {'quantizer_name': '*mlp.shared_expert_gate.*', 'enable': False}, {'quantizer_name': '*linear_attn.conv1d*', 'enable': False}, {'quantizer_name': '*mixer.conv1d*', 'enable': False}, {'quantizer_name': '*output_layer*', 'enable': False}, {'quantizer_name': 'output.*', 'enable': False}, {'quantizer_name': '*[kv]_bmm_quantizer', 'cfg': {'num_bits': (4, 3)}}], 'algorithm': {'method': 'mse', 'fp8_scale_sweep': True}}
Registered <class 'transformers.models.gemma4.modeling_gemma4.Gemma4TextAttention'> to _QuantAttention for KV Cache quantization
Inserted 1470 quantizers
100%|████████████████████████████████████████████████████████████████████████████████████████████████████████████| 512/512 [29:15<00:00,  3.43s/it]
MSE weight calibration:   0%|                                                                                              | 0/410 [00:00<?, ?it/s]Loading extension modelopt_cuda_ext_fp8...
Loaded extension modelopt_cuda_ext_fp8 in 0.5 seconds
MSE weight calibration: 100%|████████████████████████████████████████████████████████████████████████████████████| 410/410 [04:09<00:00,  1.64it/s]
Error saving quant summary: [Errno 2] No such file or directory: '/models/gemma4/google-gemma-4-31b-it-nvfp4mse-tulu3sftmixture/.quant_summary.txt'
Continuing with generation...
Saving original model config to /models/gemma4/google-gemma-4-31b-it-nvfp4mse-tulu3sftmixture
Saving processor config to /models/gemma4/google-gemma-4-31b-it-nvfp4mse-tulu3sftmixture
/root/workspace/modelopt/Model-Optimizer/examples/llm_ptq/.venv/lib/python3.12/site-packages/modelopt/torch/export/unified_export_hf.py:1256: UserWarning: Cannot export model to the model_config. The modelopt-optimized model state_dict can be saved with torch.save for further inspection.
  warnings.warn(
Traceback (most recent call last):
  File "/root/workspace/modelopt/Model-Optimizer/examples/llm_ptq/hf_ptq.py", line 1507, in <module>
    main(args)
  File "/root/workspace/modelopt/Model-Optimizer/examples/llm_ptq/hf_ptq.py", line 1466, in main
    quantize_main(
  File "/root/workspace/modelopt/Model-Optimizer/examples/llm_ptq/hf_ptq.py", line 1169, in quantize_main
    post_quantize(
  File "/root/workspace/modelopt/Model-Optimizer/examples/llm_ptq/hf_ptq.py", line 964, in post_quantize
    export_quantized(
  File "/root/workspace/modelopt/Model-Optimizer/examples/llm_ptq/hf_ptq.py", line 772, in export_quantized
    export_hf_checkpoint(
  File "/root/workspace/modelopt/Model-Optimizer/examples/llm_ptq/.venv/lib/python3.12/site-packages/modelopt/torch/export/unified_export_hf.py", line 1260, in export_hf_checkpoint
    raise e
  File "/root/workspace/modelopt/Model-Optimizer/examples/llm_ptq/.venv/lib/python3.12/site-packages/modelopt/torch/export/unified_export_hf.py", line 1194, in export_hf_checkpoint
    post_state_dict, hf_quant_config = _export_transformers_checkpoint(model, dtype)
                                       ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/root/workspace/modelopt/Model-Optimizer/examples/llm_ptq/.venv/lib/python3.12/site-packages/modelopt/torch/export/unified_export_hf.py", line 818, in _export_transformers_checkpoint
    _process_quantized_modules(model, dtype, is_modelopt_qlora)
  File "/root/workspace/modelopt/Model-Optimizer/examples/llm_ptq/.venv/lib/python3.12/site-packages/modelopt/torch/export/unified_export_hf.py", line 670, in _process_quantized_modules
    _export_quantized_weight(sub_module, dtype)
  File "/root/workspace/modelopt/Model-Optimizer/examples/llm_ptq/.venv/lib/python3.12/site-packages/modelopt/torch/export/unified_export_hf.py", line 514, in _export_quantized_weight
    and "disabled" not in repr(input_quantizer)
                          ^^^^^^^^^^^^^^^^^^^^^
  File "/root/workspace/modelopt/Model-Optimizer/examples/llm_ptq/.venv/lib/python3.12/site-packages/torch/nn/modules/module.py", line 2989, in __repr__
    extra_repr = self.extra_repr()
                 ^^^^^^^^^^^^^^^^^
  File "/root/workspace/modelopt/Model-Optimizer/examples/llm_ptq/.venv/lib/python3.12/site-packages/modelopt/torch/quantization/nn/modules/tensor_quantizer.py", line 1156, in extra_repr
    s += f" amax={self._short_amax()}"
                  ^^^^^^^^^^^^^^^^^^
  File "/root/workspace/modelopt/Model-Optimizer/examples/llm_ptq/.venv/lib/python3.12/site-packages/modelopt/torch/quantization/nn/modules/tensor_quantizer.py", line 1131, in _short_amax
    return self._short_tensor(self._amax, fmt)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/root/workspace/modelopt/Model-Optimizer/examples/llm_ptq/.venv/lib/python3.12/site-packages/modelopt/torch/quantization/nn/modules/tensor_quantizer.py", line 1136, in _short_tensor
    return f"{tensor.item():{fmt}}"
              ^^^^^^^^^^^^^
torch.AcceleratorError: CUDA error: an illegal memory access was encountered
Search for `cudaErrorIllegalAddress' in https://docs.nvidia.com/cuda/cuda-runtime-api/group__CUDART__TYPES.html for more information.
CUDA kernel errors might be asynchronously reported at some other API call, so the stacktrace below might be incorrect.
For debugging consider passing CUDA_LAUNCH_BLOCKING=1
Compile with `TORCH_USE_CUDA_DSA` to enable device-side assertions.

########
GPU 0: Peak memory usage = 15.88 GB for all processes on the GPU
GPU 1: Peak memory usage = 29.07 GB for all processes on the GPU
########
