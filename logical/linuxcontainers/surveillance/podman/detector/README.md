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

The triton container (surveillance/triton) serves the detector model - no
ultralytics/torch in the triton image. Two backends are baked in:
onnxruntime (.onnx) and tensorrt (.engine). Export the model once in the
core models-dir venv (the artifact lands in the models dir = the LXC's
/models/yolo, bind-mounted ro into triton):

    make export-onnx        # -> <models dir>/yolo26m.onnx
    make push-model         # verify it's in place

Default is the raw export (nms=False): the model's ONNX output is the
pre-NMS raw tensor [84, 8400] and the detector client runs conf filter +
NMS + class filter around the remote inference (TRITON_MIN_CONF /
TRITON_IOU). To bake NMS into the graph instead (end2end export,
output [300, 6], the client auto-detects it):

    cd <models dir> && .venv/bin/python -c \
      "from ultralytics import YOLO; YOLO('yolo26m.pt').export(format='onnx', imgsz=640, nms=True)"

A fine-tuned .pt exports the same way; set TRITON_CLASS_NAMES for its
class names and TRITON_CLASS_FILTER to the ids to react to.

### switching between yolo26 and rtdetr (TRITON_MODEL_FAMILY)

The two model families have different I/O contracts - the client must be
told which one is being served, or the boxes come out off/clustered:

|  | yolo26 (default) | rtdetr |
|---|---|---|
| input | letterbox (aspect pad 114) | plain STRETCH to 640x640 |
| output | [84,8400] raw (client NMS) or [300,6] end2end, 640-space | [300,6] cx,cy,w,h NORMALIZED to the original frame, NMS in the graph |

So switching is three changes, all env - no code:

    # 1. triton side (triton quadlet): serve the rtdetr engine
    ACTIVE_MODEL=rtdetr-x   CONFIG_PROFILE=tensorrt      # + restart triton
    # 2. detector env file: point at the model + its contract
    TRITON_MODEL=rtdetr-x   TRITON_MODEL_FAMILY=rtdetr  # + redeploy detector
    # 3. (optional) TRITON_CLASS_NAMES if the model is fine-tuned

Switching BACK to yolo26 is the mirror image (ACTIVE_MODEL=yolo26x,
CONFIG_PROFILE=onnx, TRITON_MODEL=yolo26x, TRITON_MODEL_FAMILY=yolo or
unset - the default is yolo).

Verified (rtdetr-l, bus.jpg 810x1080): bus box conf 0.955,
(13,232)-(804,732) - matches the yolo26 ground truth on the same frame.

Faster still: a TensorRT .engine (FP16). The .plan is locked to the
TensorRT version that built it - build it with the triton image's own
trtexec inside the LXC (then restart triton; the quadlet's
CONFIG_PROFILE=tensorrt + ACTIVE_MODEL pick the engine profile):

    lxc exec $(LXC) -- podman run --rm --device nvidia.com/gpu=all \
      -v /models/yolo:/src:ro -v /var/tmp:/out \
      --entrypoint /opt/tritonserver/backends/tensorrt/bin/trtexec \
      registry.linole.org/surveillance/triton:latest \
      --onnx=/src/<model>.onnx --saveEngine=/out/<model>.engine --fp16
    lxc file push $(LXC):/var/tmp/<model>.engine /ssd/models/yolo/

Measured on the 5060 Ti: with tritonserver + the FP16 .engine, GPU
utilization sits at 0-10% vs 10-40% with the old in-process
ultralytics (torch) path.

### run / deploy

    make build_and_deploy   # LXC: build+push; core: push the quadlet, restart

The detector's triton health gate (Detector.load) retries triton readiness
for 120s on startup - deploy the model + triton first (see the cameraagent
README's deploy order).
