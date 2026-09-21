## model

https://docs.ultralytics.com/models/yolo26
https://docs.ultralytics.com/quickstart

### download
cd /ssd/llm/models/detector
curl -LsSf https://astral.sh/uv/install.sh | sh
uv venv --python 3.12 --seed --managed-python
source .venv/bin/activate
uv pip install ultralytics

python -c "from ultralytics import YOLO; YOLO(\"yolo26x.pt\"); print(\"downloaded\")"

### export for triton (.pt -> .onnx)

The triton container (surveillance/triton, onnxruntime backend) serves the
detector as an ONNX model - no ultralytics in the triton image. Export once
in the same venv (the .onnx lands in the models dir = the LXC's /models):

    make export-onnx        # -> <models dir>/yolo26m.onnx
    make push-model         # verify it's in place

Default is the raw export (nms=False): the model's ONNX output is the
pre-NMS raw tensor [84, 8400] and the detector client runs conf filter +
NMS + class filter around the remote inference (DETECTOR_MIN_CONF /
DETECTOR_NMS_IOU). To bake NMS into the graph instead (end2end export,
output [300, 6], the client auto-detects it):

    cd <models dir> && .venv/bin/python -c \
      "from ultralytics import YOLO; YOLO('yolo26m.pt').export(format='onnx', imgsz=640, nms=True)"

A fine-tuned .pt exports the same way; set DETECTOR_CLASS_NAMES for its
class names and DETECTOR_CLASS to the ids to react to.

### run / deploy

    make build_and_deploy   # LXC: build+push; core: push the quadlet, restart

The detector's triton health gate (Detector.load) retries triton readiness
for 120s on startup - deploy the model + triton first (see the cameraagent
README's deploy order).
