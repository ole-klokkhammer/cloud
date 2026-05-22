# fp4-hybrid

## setup
cd ~/workspace
mkdir llmcompressor 
uv venv .venv
source .venv/bin/activate
uv pip install llmcompressor

## export 

python3 -m llmcompressor.export_hf \
    --model-path /models/gemma4/google-gemma-4-31B-it \
    --quantization fp4 \
    --output-path /models/gemma4/google-gemma-4-31B-it-fp4hybrid
