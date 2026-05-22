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

