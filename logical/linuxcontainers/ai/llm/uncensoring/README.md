# uncensoring

## heretic

https://github.com/p-e-w/heretic
https://github.com/p-e-w/heretic/pull/287

## use

git clone https://github.com/p-e-w/heretic.git
cd heretic
uv run heretic --model  /models/gemma4/google-gemma-4-31B-it-text-only \
    --device-map auto \
    --max-memory '{ "0": "29GB", "1": "12GB", "cpu": "128GB" }'

## abliterix
https://huggingface.co/wangzhang/gemma-4-31B-it-abliterated

## pre made models

https://huggingface.co/TrevorJS/gemma-4-31B-it-uncensored

https://huggingface.co/llmfan46/gemma-4-31B-it-uncensored-heretic

https://huggingface.co/coder3101/gemma-4-31B-it-heretic

https://huggingface.co/huihui-ai/Huihui-gemma-4-31B-it-abliterated-v2

