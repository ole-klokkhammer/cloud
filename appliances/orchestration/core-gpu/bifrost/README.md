# bifrost

OpenAI-compatible AI gateway for llama.cpp via [Bifrost](https://github.com/maximhq/bifrost).

Replaces LiteLLM with a high-performance Go-based proxy. Listens on port 4000 and forwards
requests to llama.cpp at `localhost:8080/v1`.

> Bifrost is written in Go. The `@maximhq/bifrost` npm package is the official distribution
> mechanism — it downloads and wraps the Go binary for your platform during `npm install`.

## Setup

```bash
# Install Node.js, npm, and bifrost on the server
make install

# Push service and config files, then enable the service
make deploy
```

## Commands

```bash
make deploy   # Copy service/config files and enable
make install  # Install bifrost via npm
make restart  # Restart the service
make status   # Check service status
make logs     # View recent logs
```

## Configuration

Provider settings are in `config.json`. The `openai` provider is configured with:
- `base_url`: `http://localhost:8080/v1` (llama.cpp)
- `models`: `qwen3-coder-next`
- `default_request_timeout_in_seconds`: `600`

Update `config.json` and run `make deploy` to apply changes.

The `sk-dummy` API key is intentional — llama.cpp does not require authentication on its
local endpoint. Bifrost requires a non-empty key value to be configured.

## Migration from LiteLLM

Bifrost exposes the same OpenAI-compatible API on port 4000. Clients pointed at
`http://<host>:4000/v1` require no changes. To call chat completions:

```bash
curl http://localhost:4000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model": "openai/qwen3-coder-next", "messages": [{"role": "user", "content": "Hello"}]}'
```
