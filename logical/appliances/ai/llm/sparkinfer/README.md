# sparkinfer
https://huggingface.co/gittensor-model-hub/Qwen3.8-27B-NVFP4-RTX5090

## install
git clone https://github.com/gittensor-ai-lab/sparkinfer && cd sparkinfer

sudo apt update
sudo apt install -y g++-12
curl -fsSL https://sh.rustup.rs | sh

cmake -B build -DCMAKE_CUDA_ARCHITECTURES=120 -DBUILD_SERVER=ON && cmake --build build -j

## start
./build/server/sparkinfer_server \
  -m /models/qwen3.8/gittensor-model-hub_Qwen3.8-27B-NVFP4-RTX5090 \
  --tokenizer /models/qwen3.8/gittensor-model-hub_Qwen3.8-27B-NVFP4-RTX5090/tokenizer.json \
  --ctx 262144 --host 0.0.0.0 --port 8000