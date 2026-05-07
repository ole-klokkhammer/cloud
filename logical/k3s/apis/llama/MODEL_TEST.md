# models

rx 470:
* q2 quantizations utilize less memory and shaders
* q4 quantizations results in memory bottleneck and are slow 
* f32 works great
* int4 also works good

## phi
- https://techcommunity.microsoft.com/blog/educatordeveloperblog/a-better-phi-family-is-coming---multi-language-support-better-vision-intelligenc/4224181
- https://huggingface.co/gabriellarson/Phi-mini-MoE-instruct-GGUF/blob/main/Phi-mini-MoE-instruct-Q8_0.gguf

### f32
https://huggingface.co/collections/Joseph717171/gguf-llama-31-8b-instruct-based-oq8-0ef32-iquants-66dfaff65a38a26f1665ed01

#### small and fast
- prabal123/Tinyllama-2-f32bit

#### LLAMA
- Joseph717171/Llama-3.1-SuperNova-Lite-8.0B-OQ8_0-F32.EF32.IQ4_K-Q8_0-GGUF
https://huggingface.co/Joseph717171/Llama-3.1-SuperNova-Lite-8.0B-OQ8_0-F32.EF32.
IQ4_K-Q8_0-GGUF/blob/main/Llama-3.1-SuperNova-Lite-8.0B-OQ8_0.EF32.IQ4_K_M.gguf
Very fast

- Joseph717171/Llama-3.2-3B-Instruct-OQ8_0-F32.EF32.IQ4_K-Q8_0-GGUF
- Llama-3.2-3B-Instruct-OF32.EF32.IQ8_0.gguf
https://huggingface.co/Joseph717171/Llama-3.2-3B-Instruct-OQ8_0-F32.EF32.IQ4_K-Q8_0-GGUF 
 

- Joseph717171/DeepHermes-3-Llama-3.2-3B-Preview-OQ8_0-F32.EQ8_0-F32.IQ4_K-Q8_0-GGUF
- DeepHermes-3-Llama-3-3B-Preview-OF32.EF32.IQ8_0.gguf
https://huggingface.co/Joseph717171/DeepHermes-3-Llama-3.2-3B-Preview-OQ8_0-F32.EQ8_0-F32.IQ4_K-Q8_0-GGUF

- xtuner/llava-llama-3-8b-v1_1-gguf
- llava-llama-3-8b-v1_1-int4.gguf
https://huggingface.co/xtuner/llava-llama-3-8b-v1_1-gguf

#### phi 
- Mungert/Phi-4-mini-instruct.gguf
- phi-4-mini-bf16-q8.gguf

##### vision
- abetlen/Phi-3.5-vision-instruct-gguf
Phi-3.5-3.8B-vision-instruct-F16.gguf
https://huggingface.co/abetlen/Phi-3.5-vision-instruct-gguf



#### qwen 2.5 vision
- mradermacher/qwen-vision-2.5-GGUF
- qwen-vision-2.5.Q4_K_M.gguf
https://huggingface.co/mradermacher/qwen-vision-2.5-GGUF


#### deepseek
- unsloth/DeepSeek-R1-0528-Qwen3-8B-GGUF
- DeepSeek-R1-0528-Qwen3-8B-Q4_K_M.gguf
memory bottleneck, but also works slow but fine

#### Mistral
- MaziyarPanahi/Mistral-Small-Instruct-2409-GGUF
- Mistral-Small-Instruct-2409.IQ2_XS.gguf
low gpu utilization. slow token/sec, but works fine