# Models


1. Minimax M2.1
   - numactl --interleave=all llama-server \
  --host 0.0.0.0 \
  --port 8080 \
  -m /models/MiniMax-M2.1-Q4_K_M-00001-of-00003.gguf \
  -n 2048 \
  -t 16 \
  --no-mmap \
  --mlock \
  --n-gpu-layers 6 \
  --flash-attn on \
  --cache-type-k q4_0 \
  --cache-type-v q4_0 \
  -c 200000 \
  --temp 1 \
  --top_p 0.95 \
  --top_k 40 \
  --repeat_penalty 1.25

2. NousResearch_NousCoder-14B-Q8_0.gguf
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
  -c 8192 \
  --temp 0.45 \
  --top_p 0.95 \
  --top_k 40
3. devstral 2 small
4. GLM-4.7