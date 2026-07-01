# llama.cpp

## setup
sudo apt update
sudo apt install -y build-essential cmake git libcurl4-openssl-dev 

wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2404/x86_64/cuda-keyring_1.1-1_all.deb
sudo dpkg -i cuda-keyring_1.1-1_all.deb
sudo apt-get update
sudo apt-get -y install cuda-toolkit-13-3

echo 'export PATH=/usr/local/cuda/bin:$PATH' >> ~/.bashrc
echo 'export LD_LIBRARY_PATH=/usr/local/cuda/lib64:$LD_LIBRARY_PATH' >> ~/.bashrc
source ~/.bashrc

nvcc --version


### build locally
https://github.com/ggml-org/llama.cpp/blob/master/docs/build.md

mkdir ~/workspace 
cd ~/workspace

git clone https://github.com/ggml-org/llama.cpp.git
cd llama.cpp

#### cuda build

cmake -B build -DGGML_CUDA=ON -DCMAKE_CUDA_ARCHITECTURES=native -DLLAMA_CURL=1
cmake --build build --config Release -j$(nproc)

sudo ln -sf $(pwd)/build/bin/llama-server /usr/local/bin/llama-server
sudo ln -sf $(pwd)/build/bin/llama-cli /usr/local/bin/llama-cli


### verification
llama-server --version

check for 
CUDA
AVX
AVX2

## enable service
sudo nano llama-server.service
---

sudo systemctl daemon-reload
sudo systemctl enable --now ./llama-server

sudo systemctl status llama-server 
sudo journalctl -u llama-server -f



## testing
/usr/local/bin/llama-server \
      --host 0.0.0.0 \
      --port 8080 \
      -m /models/Qwen3-Coder-Next/Qwen3-Coder-Next-IQ4_NL.gguf \
      -c 128000 \
      -n 8192 \
      --cache-type-k q4_0 --cache-type-v q4_0 \
      --tensor-split 33,15 \
      --n-gpu-layers 99 \
      -t 16 \
      --flash-attn on \
      --parallel 1 \
      --no-mmap \
      --mlock \
      --jinja \
      --reasoning-budget 0 \
      --temp 1 \
      --top-p 0.95 \
      --top-k 40 \
      --repeat-penalty 1.25