#
- ghcr.io/ggml-org/llama.cpp:full-cuda
- https://github.com/ggml-org/llama.cpp/blob/master/docs/docker.md
- https://huggingface.co/unsloth/Devstral-Small-2-24B-Instruct-2512-GGUF
  
## Test ollama
mkdir -p ~/ollama

docker rm -f ollama 2>/dev/null || true
docker run -d --name ollama \
  --restart unless-stopped \
  --gpus all \
  -p 11434:11434 \
  -v ~/ollama:/root/.ollama \
  ollama/ollama:latest

docker exec -it ollama ollama list
docker exec -it ollama ollama run devstral-small-2:latest 

## temp testing
 
### small
docker run --name llama-api \
  --restart unless-stopped \
  --network host \
  --gpus all \
  -v ~/llama-api/models:/models \
  ghcr.io/ggml-org/llama.cpp:full-cuda \
  --server \
  --host 0.0.0.0 \
  --port 8080 \
  -m /models/Devstral-Small-2-24B-Instruct-2512-Q4_K_M.gguf \
  -n 1024 \
  -t 12 \
  --n-gpu-layers -1 \
  -c 16384 \
  -b 512 \
  --temp 0.15

### large
numactl --interleave=all docker run --name llama-api \
  --restart unless-stopped \
  --network host \
  --gpus all \
  --cap-add IPC_LOCK \
  --ulimit memlock=-1:-1 \
  -v ~/llama-api/models:/models \
  ghcr.io/ggml-org/llama.cpp:full-cuda \
  --server \
  --host 0.0.0.0 \
  --port 8080 \
  -m /models/MiniMax-M2-Q4_K_M-00001-of-00003.gguf \
  -n 1024 \
  -t 16 \
  --mlock \
  --mmap \
  --n-gpu-layers 7 \
  --numa distribute \
  --flash-attn on \
  --cache-type-k q4_0 \
  --cache-type-v q4_0 \
  -b 512 \
  -c 4096 \
  --temp 1 \
  --top_p 0.95 \
  --top_k 40 


### systemd

// mmap
llama-server \
  --host 0.0.0.0 \
  --port 8080 \
  -m /models/MiniMax-M2-Q4_K_M-00001-of-00003.gguf \
  -n 1024 \
  -t 16 \
  --mlock \
  --mmap \
  --n-gpu-layers 7 \
  --numa distribute \
  --flash-attn on \
  --cache-type-k q4_0 \
  --cache-type-v q4_0 \
  -b 512 \
  -c 8096 \
  --temp 1 \
  --top_p 0.95 \
  --top_k 40 


// equal interleaving
numactl --interleave=all llama-server \
  --host 0.0.0.0 \
  --port 8080 \
  -m /models/MiniMax-M2-Q4_K_M-00001-of-00003.gguf \
  -n 1024 \
  -t 16 \
  --no-mmap \
  --mlock \
  --numa distribute \
  --n-gpu-layers 7 \
  --flash-attn on \
  --cache-type-k q4_0 \
  --cache-type-v q4_0 \
  -b 512 \
  -c 8096 \
  --temp 1 \
  --top_p 0.95 \
  --top_k 40 