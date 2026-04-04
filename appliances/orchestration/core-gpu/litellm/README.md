# litellm

Anthropic API proxy for llama.cpp via LiteLLM.

## Setup

```bash
# Install litellm on the server
make install

# Deploy and enable the service
make deploy
```

## Commands

```bash
make deploy   # Copy service file and enable
make install  # Install litellm via pip
make restart  # Restart the service
make status   # Check service status
make logs     # View recent logs
```
