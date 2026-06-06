# testing

uv venv .venv
source .venv/bin/activate

uv pip install lm-eval transformers
uv pip install torch --index-url https://download.pytorch.org/whl/cu132

OPENAI_API_KEY=dummy \
lm_eval --model openai-completions \
  --model_args model=Gemma4-31b-it,base_url=https://llm.linole.org,tokenizer=/models/gemma4/google-gemma-4-31b-it-nvfp4mse,tokenizer_backend=huggingface \
  --tasks wikitext \
  --batch_size 1 \
  --output_path ./results/nvfp4mse

lm_eval --model local-completions \
  --tasks gsm8k \
  --model_args \
  model=google/gemma-4-31b-it,base_url=http://192.168.10.151:8000/v1/completions,num_concurrent=1,max_retries=3,tokenized_requests=False,batch_size=16
