# TensorRT-LLM

## References
https://nvidia.github.io/TensorRT-LLM/installation/linux.html

## Setup

```bash
# Clone repo
cd ~/workspace
git clone https://github.com/NVIDIA/TensorRT-LLM.git
cd TensorRT-LLM
```

### Install (pip — fastest)

```bash
uv venv --python 3.12 --seed
source .venv/bin/activate

# Install TensorRT-LLM (includes torch, tensorrt, etc.)
pip install tensorrt-llm
```

### Install (from source — if pip doesn't support sm_120/Blackwell)

```bash
uv venv --python 3.12 --seed
source .venv/bin/activate

pip install -r requirements-dev.txt
python3 scripts/build_wheel.py --cuda_architectures "120-real"
pip install build/tensorrt_llm*.whl
```

## Verify

```bash
cd ~ 
python3 -c "import tensorrt_llm; print(tensorrt_llm.__version__)"
python3 -c "import torch; print(torch.cuda.get_device_name(0))"
```

## Check supported models

```bash
python3 -c "
from tensorrt_llm.models import MODEL_MAP
for k in sorted(MODEL_MAP):
    print(k)
"
```

## Check Qwen3-Coder-Next support

```bash
# Check model architecture
pip install huggingface-hub
python3 -c "
from huggingface_hub import hf_hub_download
import json
path = hf_hub_download('Qwen/Qwen3-Coder-Next', 'config.json')
cfg = json.load(open(path))
print('architectures:', cfg.get('architectures'))
print('model_type:', cfg.get('model_type'))
"

# Then check if MODEL_MAP has that architecture
apt install -y libopenmpi-dev openmpi-bin
python3 -c "
from tensorrt_llm.models import MODEL_MAP
for k in sorted(MODEL_MAP):
    if any(x in k.lower() for x in ['qwen', 'mamba', 'jamba', 'ssm', 'hybrid']):
        print(k)
"
```

## qwen3 next on tensorrt blackwell
https://nvidia.github.io/TensorRT-LLM/deployment-guide/deployment-guide-for-qwen3-next-on-trtllm.html

