# OpenCode

AI coding assistant using a local Qwen3 Coder Next model via llama-server.

- **CLI**: `~/.opencode/bin/opencode` (v1.3.15)
- **VSCode extension**: `tanishqkancharla.opencode-vscode`
- **Model**: Qwen3-Coder-Next-IQ4_NL.gguf served at `https://llm.linole.org/v1`
- **Config**: [opencode.json](../../opencode.json) in project root

## Setup

### 1. Install CLI

```bash
# see https://opencode.ai for install instructions, then verify:
opencode --version
```

### 2. Add to PATH

Add the opencode bin directory to `~/.profile` (not `.bashrc`) so it's available to
VSCode, desktop sessions, and all shells:

```bash
echo 'export PATH="$HOME/.opencode/bin:$PATH"' >> ~/.profile
```

> **Important:** Bash login shells source `~/.bash_profile` *instead of* `~/.profile`
> when both exist. If you have a `~/.bash_profile`, make sure it sources `~/.profile`:
>
> ```bash
> # ~/.bash_profile
> [ -f "$HOME/.profile" ] && . "$HOME/.profile"
> [ -f "$HOME/.bashrc" ] && . "$HOME/.bashrc"
> ```
>
> Without this, VSCode and other GUI-launched programs won't see `opencode` on PATH.

### 3. VSCode extension

Install `tanishqkancharla.opencode-vscode` from the marketplace. It calls the CLI
under the hood — no extra config needed, it reads `opencode.json` from the workspace.

After installing or changing PATH, **restart VSCode** (or launch it from a terminal
with `code .`) so it picks up the new PATH.