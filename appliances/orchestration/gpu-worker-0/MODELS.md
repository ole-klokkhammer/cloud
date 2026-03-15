# Models


1. Minimax M2.1 https://huggingface.co/unsloth/MiniMax-M2.1-GGUF
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
      --jinja \
      --temp 1 \
      --top_p 0.95 \
      --top_k 40 \
      --repeat_penalty 1.25

     IQ2 runs more in a loop on the same question compared to Q4, but was fixed with --jinja
   - numactl --interleave=all llama-server \
      --host 0.0.0.0 \
      --port 8080 \
      -m /models/MiniMax-M2.1-UD-IQ2_M-00001-of-00002.gguf \
      -n 8096 \
      -t 16 \
      --no-mmap \
      --mlock \
      --n-gpu-layers 10 \
      --flash-attn on \
      --cache-type-k q4_0 \
      --cache-type-v q4_0 \
      -c 200000 \
      --jinja \
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
4. nvidia nemotron 3 nano ->>> VERY good explanations, what about implementation?
   - numactl --interleave=all llama-server \
      --host 0.0.0.0 \
      --port 8080 \
      -m /models/Nemotron-3-Nano-30B-A3B-Q8_0.gguf \
      -n 64000 \
      -t 16 \
      --no-mmap \
      --mlock \
      --n-gpu-layers 20 \
      --flash-attn on \
      -c 200000 \
      --jinja \
      --temp 1.0 \
      --top_p 1.0
5. https://huggingface.co/miromind-ai/MiroThinker-v1.5-235B
6. GLM-4.7-UD-IQ2_M-00001-of-00003.gguf
   - numactl --interleave=all llama-server \
      --host 0.0.0.0 \
      --port 8080 \
      -m /models/GLM-4.7-UD-IQ2_M-00001-of-00003.gguf \
      -n 8096 \
      -t 16 \
      --no-mmap \
      --mlock \
      --n-gpu-layers 10 \
      --flash-attn on \
      --cache-type-k q4_0 \
      --cache-type-v q4_0 \
      -c 200000 \
      --jinja \
      --temp 1 \
      --top_p 0.95 \
      --top_k 40 \
      --repeat_penalty 1.25

7. qwen 3 coder next
   - numactl --interleave=all llama-server \
      --host 0.0.0.0 \
      --port 8080 \
      -m /models/Qwen3-Coder-Next-Q4_K_S.gguf \
      -n 8096 \
      -t 16 \
      --no-mmap \
      --mlock \
      --n-gpu-layers 10 \
      --flash-attn on \
      --cache-type-k q4_0 \
      --cache-type-v q4_0 \
      -c 200000 \
      --jinja \
      --temp 1 \
      --top_p 0.95 \
      --top_k 40 \
      --repeat_penalty 1.25