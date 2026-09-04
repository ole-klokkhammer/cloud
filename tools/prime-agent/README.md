# prime-agent

Local **Prime Agent** [`PrimeIntellect-ai/prime-agent`](https://github.com/PrimeIntellect-ai/prime-agent)
appliance, run as a **user-level (rootless) Podman Quadlet**.

Instead of running a headless service, it is a keep-alive "workbench" container:
the container stays up, and you drop into it to drive the interactive coding TUI
against a mounted workspace.

```
/workspace                     <- your git repo (RW bind) -> the agent's CWD
/home/agent/.prime/agent       <- persistent named volume (sessions, auth, kernel venv)
.../agent/models.json          <- repo copy, bind-mounted read-only (source of truth)
```

## Files

| File | Purpose |
| :-- | :-- |
| [`podman/prime-agent.container`](podman/prime-agent.container) | The Quadlet -> user service `prime-agent.service` |
| [`podman/Dockerfile`](podman/Dockerfile) | Slim `node:22-slim` image wrapping the official installer |
| [`podman/models.json`](podman/models.json) | LLM provider config (`qwen-local`) |
| [`podman/makefile`](podman/makefile) | Local lifecycle: image / deploy / status / logs / exec |
| [`agent.sh`](agent.sh) | Register **one service per workspace** (Model B) |

## One-time setup

```bash
# User-level services auto-start only if the user has lingering enabled.
loginctl enable-linger $USER

# Build the image (podman/ is the build context; Dockerfile + models.json are there).
cd podman && make image
```

## Run

```bash
cd podman
make deploy          # install the quadlet, daemon-reload, start the service
make status          # user service + container state
make exec            # enter the keep-alive container -> interactive TUI on /workspace
```

Inside the TUI, pick the provider/model. The local provider is available as
`qwen-local` / model `Qwen3.8-27b`, pointed at `https://llm.linole.org/v1`.

## Changing the workspace

Edit the host path in [`podman/prime-agent.container`](podman/prime-agent.container)
(the `Volume=...:/workspace:rw` line), then `make deploy`. By default it attachses
the cloud repo:

```
/home/ole/workspace/oleklokkhammer/projects/cloud  -> /workspace
```

## Changing the LLM / model

- **Edit the provider** — tweak `baseUrl` / `models` in
  [`podman/models.json`](podman/models.json), then `make deploy` (it is a live host
  bind; no image rebuild needed).
- **Add auth** — the `qwen-local` provider references the `LOCAL_LLM_KEY` env var;
  the current gateway ignores it (set to `dummy`). If your backend starts requiring a
  key, put the real value in the `Environment=LOCAL_LLM_KEY=...` line of the quadlet.

## Update the agent

```bash
cd podman && make redeploy   # rebuild image (new version/channel) + redeploy
# or pin a release:
docker build --build-arg PRIME_AGENT_VERSION=<ver> -t prime-agent:latest podman
```

## Logs & teardown

```bash
make logs          # journalctl tail of the user service
make clean         # stop + remove the container and its state volume (wipes sessions)
```

> `make clean` deletes the `prime-agent-state` volume — i.e. agent sessions,
> `auth.json`, and the kernel venv. Use it only when you want a fresh agent.

## One service per workspace — `agent.sh`

The static quadlet above attaches a *single* workspace. When you want **N
workspaces, each with its own running agent**, `agent.sh` generates a
dedicated quadlet per workspace (Model B: one service per workspace, keep-alive
+ manual start):

```bash
agent.sh <workspace-path> [slug]        # register + start prime-agent-<slug>
agent.sh list                           # show every registered workspace
agent.sh exec <slug>                    # enter that workbench → interactive TUI
agent.sh remove <slug>                  # stop + unregister + drop its state volume
```

What it does for `agent.sh <path>`:

- writes `~/.config/containers/systemd/prime-agent-<slug>.container` (slug
  defaults to the lowercased workspace basename), with `Volume=<path>:/workspace:rw`
  and its own `prime-agent-<slug>-state` volume,
- `systemctl --user daemon-reload` so the quadlet generator materializes the
  first-class unit `prime-agent-<slug>.service`,
- starts it (keep-alive: `Exec=sleep infinity`).

Each workspace therefore runs in isolation (separate container + state volume);
`agent.sh list` shows them all with their live status. The `makefile` XDG
shielding is re-implemented inside `agent.sh`, so registration works even
launched from the snap-confined VS Code terminal.

## Notes / troubleshooting

- **First run provisions the IPython kernel.** Prime Agent provisions its RLM kernel
  into the state volume on the first interactive use. It is deliberately *not* baked
  into the image, so it persists across image rebuilds.
- **Rootless network is host.** The agent makes only outbound calls; no ports are
  published. If `https://llm.linole.org` is unreachable from the host, check host
  firewall/VPN before touching the container.
- **`prime-agent` not found after rebuild** — the installer places the binary on
  PATH inside the image; if it's missing, rebuild with `make image` and re-`deploy`.
- **Workspace writes don't appear on host** — confirm the host path exists and the
  `rw` bind in the quadlet points at it; `podman exec prime-agent sh -c 'touch /workspace/.writetest'`.

## Out of scope

LXC `profile.yaml` (this deploy targets this machine, not a container), GPU
pass-through (the agent is CPU-only), and interactive-TUI automation (only how-to,
not wired).
