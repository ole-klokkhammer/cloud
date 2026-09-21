# triton - inference server (YOLO model host)

## download models

curl -LsSf https://astral.sh/uv/install.sh | sh
uv venv --python 3.12 --seed --managed-python
source .venv/bin/activate
uv pip install ultralytics-opencv-headless

nano download.py
from ultralytics import RTDETR
rtdetr = RTDETR("rtdetr-l.pt")

nano convert.py
from ultralytics import RTDETR
rtdetr = RTDETR("rtdetr-l.pt")
rtdetr.export(format="engine", device=1, quantize=16)

## convert to tensortrt
sudo podman run --rm -it \
  --device nvidia.com/gpu=all \
  -v /models/yolo:/models \
  --entrypoint sh \
  nvcr.io/nvidia/tritonserver:25.08-py3 \
  -c "/usr/src/tensorrt/bin/trtexec --onnx=/models/rtdetr-x.onnx \
    --saveEngine=/models/rtdetr-x.plan --fp16"