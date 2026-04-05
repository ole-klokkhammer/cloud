# bifrost

Anthropic API gateway for llama.cpp via [Bifrost](https://github.com/maximhq/bifrost).

## Setup

```bash
# Install Node.js and pre-cache the bifrost package
make install

# Deploy and enable the service
make deploy

# Register the llama.cpp provider (one-time, after service is up)
make configure
```

Or configure the provider manually via the web UI at `http://core-gpu.home.lan:4000`.

## Provider config

| Field               | Value                        |
|---------------------|------------------------------|
| Name                | `llama-local`                |
| Base provider type  | `openai`                     |
| Base URL            | `http://localhost:8080/v1`   |
| API key             | `sk-dummy`                   |

## Commands

```bash
make deploy     # Copy service file and enable
make install    # Install Node.js and cache bifrost
make configure  # Register llama.cpp provider via API
make restart    # Restart the service
make status     # Check service status
make logs       # View recent logs
```

## Architecture

```
Client (Claude Code)
    |
    v  :4000/anthropic
Bifrost Gateway
    |
    v  localhost:8080/v1
llama.cpp Server
```
