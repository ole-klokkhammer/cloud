# claude

## setup
curl -fsSL https://claude.ai/install.sh | bash

##  Add to profile
nano ~/.bashrc

>>
export ANTHROPIC_BASE_URL="http://core-gpu.home.lan:4000"
export ANTHROPIC_CUSTOM_MODEL_OPTION="qwen3-coder-next"


##  Add to vscode
vscode settings.json

>>
"claudeCode.environmentVariables": [
    {
        "name": "ANTHROPIC_BASE_URL",
        "value": "http://core-gpu.home.lan:4000"
    },
    {
        "name": "ANTHROPIC_CUSTOM_MODEL_OPTION",
        "value": "qwen3-coder-next"
    },
    {
        "name": "ANTHROPIC_CUSTOM_MODEL_OPTION_NAME",
        "value": "Qwen3 Coder Next (local)"
    },
    {
        "name": "CLAUDE_TEMPERATURE",
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