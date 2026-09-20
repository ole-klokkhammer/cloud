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
