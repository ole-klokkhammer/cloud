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

### 4. Open the chat panel

- **Activity Bar**: Click the OpenCode icon in the left sidebar
- **Command Palette**: `Ctrl+Shift+P` → *OpenCode: Open Panel*
- **From terminal**: Launch VSCode with `code .` from a directory containing `opencode.json`

The panel starts an `opencode serve` process in the background and connects to it.

## Configuration

The extension reads `opencode.json` from the workspace root:

```json
{
    "$schema": "https://opencode.ai/config.json",
    "model": "llama.cpp/Qwen3-Coder-Next-IQ4_NL.gguf",
    "provider": {
        "llama.cpp": {
            "npm": "@ai-sdk/openai-compatible",
            "name": "llama-server (local)",
            "options": {
                "baseURL": "https://llm.linole.org/v1"
            },
            "models": {
                "Qwen3-Coder-Next-IQ4_NL.gguf": {
                    "name": "Qwen3 Coder Next (local)"
                }
            }
        }
    }
}
```

Key fields:
- **`model`**: `<provider>/<model-id>` — references a provider and model defined below
- **`provider.<name>.npm`**: The AI SDK adapter package (use `@ai-sdk/openai-compatible` for llama.cpp)
- **`provider.<name>.options.baseURL`**: The OpenAI-compatible API endpoint
- **`provider.<name>.models`**: Map of model IDs to display names

### Troubleshooting: `spawn opencode ENOENT` in VSCode

The VSCode extension spawns `opencode` using the **extension host's** `process.env`,
which inherits PATH from how VSCode was launched — not from the integrated terminal.
If VSCode was opened from a desktop shortcut or file manager, `~/.profile` and
`~/.bashrc` are typically **not** sourced, so `~/.local/bin` and `~/.opencode/bin`
may be missing from PATH.

**Fix:** Symlink to `/usr/local/bin` (always on PATH):

```bash
sudo ln -sf ~/.local/bin/opencode /usr/local/bin/opencode
```

Then reload VSCode (`Ctrl+Shift+P` → *Developer: Reload Window*).

**Verify:**

```bash
# In a regular terminal — should already work:
which opencode && opencode --version

# If you need to check what VSCode sees, open its Developer Tools
# (Help → Toggle Developer Tools) and run in the console:
# process.env.PATH
```