# claude

## setup
curl -fsSL https://claude.ai/install.sh | bash

##  Add to profile
nano ~/.bashrc

>>
export ANTHROPIC_BASE_URL="http://core-gpu.home.lan:4000/anthropic"
export ANTHROPIC_CUSTOM_MODEL_OPTION="llama-local/qwen3-coder-next"
export ANTHROPIC_CUSTOM_MODEL_OPTION_NAME="Qwen3 Coder Next (local)"
export ANTHROPIC_TEMPERATURE="1"
export ANTHROPIC_TOP_P="0.95"
export ANTHROPIC_TOP_K="40"


##  Add to vscode
vscode settings.json

>>
"claudeCode.environmentVariables": [
    {
        "name": "ANTHROPIC_BASE_URL",
        "value": "http://core-gpu.home.lan:4000/anthropic"
    },
    {
        "name": "ANTHROPIC_CUSTOM_MODEL_OPTION",
        "value": "llama-local/qwen3-coder-next"
    },
    {
        "name": "ANTHROPIC_CUSTOM_MODEL_OPTION_NAME",
        "value": "Qwen3 Coder Next (local)"
    },
    {
        "name": "ANTHROPIC_TEMPERATURE",
        "value": "1"
    },
    {
        "name": "ANTHROPIC_TOP_P",
        "value": "0.95"
    },
    {
        "name": "ANTHROPIC_TOP_K",
        "value": "40"
    }
]