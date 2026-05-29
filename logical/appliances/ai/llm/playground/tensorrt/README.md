# TensorRT-LLM

## References
https://nvidia.github.io/TensorRT-LLM/installation/linux.html

### install
python3 -m venv .venv
source .venv/bin/activate

python -m pip install --upgrade pip setuptools wheel
python -m pip install torch==2.10.0 torchvision --index-url https://download.pytorch.org/whl/cu130
python -m pip install transformers==5.5.3
python -m pip install tensorrt_llm==1.3.0rc14


### quantize
git clone https://github.com/NVIDIA/TensorRT-LLM.git

cd /path/to/TensorRT-LLM

### run
https://github.com/NVIDIA/TensorRT-LLM/blob/main/examples/auto_deploy/model_registry/configs/gemma4_dense.yaml

UDA_DEVICE_ORDER=PCI_BUS_ID CUDA_VISIBLE_DEVICES=1 trtllm-serve serve   /models/gemma4/AEON-7-Gemma-4-31B-it-DECKARD-HERETIC-Uncensored-NVFP4   --backend trt   --extra_llm_api_options ~/workspace/tensorrt/gemma4_dense.yaml


https://nvidia.github.io/TensorRT-LLM/features/auto_deploy/auto-deploy.html
cd examples/auto_deploy

python build_and_run_ad.py --model "TinyLlama/TinyLlama-1.1B-Chat-v1.0"
