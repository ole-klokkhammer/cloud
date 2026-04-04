# claude

## setup
curl -fsSL https://claude.ai/install.sh | bash

##  Add to profile
nano ~/.bashrc

>>
export ANTHROPIC_BASE_URL="http://core-gpu.home.lan:4000"
export ANTHROPIC_CUSTOM_MODEL_OPTION="qwen3-coder-next"


## Temperature

Temperature is set on the llama-server via `--temp` in `llama-server.service`.
To change temperature, edit the service file and restart the server:
```
make deploy && make restart
```

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
    }
]