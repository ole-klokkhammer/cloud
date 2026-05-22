#
- ghcr.io/ggml-org/llama.cpp:full-cuda
- https://github.com/ggml-org/llama.cpp/blob/master/docs/docker.md
- https://huggingface.co/unsloth/Devstral-Small-2-24B-Instruct-2512-GGUF
  
## Models
- minimax m2
- devstral 2 (small)
- GLM-4.7
- https://huggingface.co/Qwen/Qwen3-VL-235B-A22B-Instruct
- https://huggingface.co/Qwen/Qwen3-VL-235B-A22B-Thinking


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


## testing Devstral 2
- numactl --interleave=all llama-server \
  --host 0.0.0.0 \
  --port 8080 \
  -m /models/Devstral-2-123B-Instruct-2512-IQ4_NL-00001-of-00002.gguf \
  -n 1024 \
  -t 16 \
  --no-mmap \
  --mlock \
  --n-gpu-layers 19 \
  --flash-attn on \
  --cache-type-k q4_0 \
  --cache-type-v q4_0 \
  -b 2048 \
  -ub 1024 \
  -c 8096 \
  --temp 0.45 \
  --top_p 0.95 \
  --top_k 40


## testing Devstral 2 small
- numactl --interleave=all llama-server \
  --host 0.0.0.0 \
  --port 8080 \
  -m /models/Devstral-Small-2-24B-Instruct-2512-IQ4_NL.gguf \
  -n 1024 \
  -t 16 \
  --no-mmap \
  --mlock \
  --n-gpu-layers 999 \
  --flash-attn on \
  --cache-type-k q4_0 \
  --cache-type-v q4_0 \
  -b 2048 \
  -ub 1024 \
  -c 8096 \
  --temp 0.45 \
  --top_p 0.95 \
  --top_k 40

# IQuest-Coder-V1-40B-Instruct.Q4_K_M.gguf

- numactl --interleave=all llama-server \
  --host 0.0.0.0 \
  --port 8080 \
  -m /models/IQuest-Coder-V1-40B-Instruct.Q4_K_M.gguf \
  -n 1024 \
  -t 16 \
  --no-mmap \
  --mlock \
  --n-gpu-layers 50 \
  --flash-attn on \
  --cache-type-k q4_0 \
  --cache-type-v q4_0 \
  -b 2048 \
  -ub 1024 \
  -c 8096 \
  --temp 0.45 \
  --top_p 0.95 \
  --top_k 40

# NousResearch_NousCoder-14B-Q8_0.gguf
Better than iquest coder

- numactl --interleave=all llama-server \
  --host 0.0.0.0 \
  --port 8080 \
  -m /models/NousResearch_NousCoder-14B-Q8_0.gguf \
  -n 4096 \
  -t 16 \
  --no-mmap \
  --mlock \
  --n-gpu-layers -1 \
  --flash-attn on \
  --cache-type-k q4_0 \
  --cache-type-v q4_0 \
  -b 4096 \
  -ub 8192 \
  -c 8192 \
  --temp 0.45 \
  --top_p 0.95 \
  --top_k 40

## testing minimax m2

### Using both numa nodes in a nps2 config
limits.cpu.nodes: "0,1"
limits.cpu: "16" 

- numactl --interleave=all llama-server \
  --host 0.0.0.0 \
  --port 8080 \
  -m /models/MiniMax-M2-Q4_K_M-00001-of-00003.gguf \
  -n 1024 \
  -t 16 \
  --no-mmap \
  --mlock \
  --n-gpu-layers 7 \
  --flash-attn on \
  --cache-type-k q4_0 \
  --cache-type-v q4_0 \
  -b 512 \
  -c 8096 \
  --temp 1 \
  --top_p 0.95 \
  --top_k 40

- numactl --interleave=all llama-server \
  --host 0.0.0.0 \
  --port 8080 \
  -m /models/MiniMax-M2-Q4_K_M-00001-of-00003.gguf \
  -n 1024 \
  -t 16 \
  --no-mmap \
  --mlock \
  --n-gpu-layers 7 \
  --flash-attn on \
  --cache-type-k q4_0 \
  --cache-type-v q4_0 \
  -b 2048 \
  -ub 1024 \
  -c 8096 \
  --temp 0.45 \
  --top_p 0.95 \
  --top_k 40

- numactl --interleave=all llama-server \
  --host 0.0.0.0 \
  --port 8080 \
  -m /models/MiniMax-M2.1-Q4_K_M-00001-of-00003.gguf \
  -n 4096 \
  -t 16 \
  --no-mmap \
  --mlock \
  --n-gpu-layers 7 \
  --flash-attn on \
  --cache-type-k q4_0 \
  --cache-type-v q4_0 \
  -c 8096 \
  --temp 0.45 \
  --top_p 0.95 \
  --top_k 40

### Single node numa
in profile:
limits.cpu.nodes: "0"
raw.lxc: |
  lxc.cgroup2.cpuset.mems = 0

dont use more memory than exists on a single node = 512/2
also use physical cores, not hyperthreads. This means 8 cores per numa node.
 
command:
llama-server \
  --host 0.0.0.0 \
  --port 8080 \
  -m /models/MiniMax-M2-Q4_K_M-00001-of-00003.gguf \
  -n 1024 \
  -t 8 \
  --no-mmap \
  --mlock \
  --n-gpu-layers 7 \
  --flash-attn on \
  --cache-type-k q4_0 \
  --cache-type-v q4_0 \
  -b 512 \
  -c 8096 \
  --temp 1 \
  --top_p 0.95 \
  --top_k 40 

### Using both numa nodes in a nps2 config without gpu
limits.cpu.nodes: "0,1"

CUDA_VISIBLE_DEVICES="" numactl --interleave=all llama-server \
  --host 0.0.0.0 \
  --port 8080 \
  -m /models/MiniMax-M2-Q4_K_M-00001-of-00003.gguf \
  -n 1024 \
  -t 16 \
  --no-mmap \
  --mlock \
  --n-gpu-layers 0 \
  --flash-attn on \
  --cache-type-k q4_0 \
  --cache-type-v q4_0 \
  -b 512 \
  -c 8096 \
  --temp 1 \
  --top_p 0.95 \
  --top_k 40 

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


// single numa node only
numactl --cpunodebind=0 --membind=0 llama-server \
  --host 0.0.0.0 \
  --port 8080 \
  -m /models/MiniMax-M2-Q4_K_M-00001-of-00003.gguf \
  -n 1024 \
  -t 8 \
  --numa isolate \
  --no-mmap \
  --mlock \
  --n-gpu-layers 7 \
  --flash-attn on \
  --cache-type-k q4_0 \
  --cache-type-v q4_0 \
  -b 512 \
  -c 8096 \
  --temp 1 \
  --top_p 0.95 \
  --top_k 40

// cpu and system ram only
numactl --cpunodebind=0 --membind=0 llama-server \
  --host 0.0.0.0 \
  --port 8080 \
  -m /models/MiniMax-M2-Q4_K_M-00001-of-00003.gguf \
  -n 1024 \
  -t 8 \
  --numa isolate \
  --no-mmap \
  --mlock \
  --n-gpu-layers 0 \
  --flash-attn on \
  --cache-type-k q4_0 \
  --cache-type-v q4_0 \
  -b 512 \
  -c 8096 \
  --temp 1 \
  --top_p 0.95 \
  --top_k 40