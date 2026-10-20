# prime-agent

Local **Prime Agent** [`PrimeIntellect-ai/prime-agent`](https://github.com/PrimeIntellect-ai/prime-agent)
appliance, run as **rootless `podman compose`** projects — one compose project
per registered workspace, generated and driven by [`agent.sh`](agent.sh).

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
| [`agent.sh`](agent.sh) | Register **one compose project per workspace** + lifecycle |
| [`podman/Dockerfile`](podman/Dockerfile) | `node:24` image wrapping the official installer |
| [`podman/build.sh`](podman/build.sh) | Builds `prime-agent:latest` (context = `podman/`) |
| [`podman/models.json`](podman/models.json) | LLM provider config (`qwen-local`), bind-mounted live |

## How it works

`agent.sh <workspace-path> [slug]` writes a compose project to
`~/.config/prime-agent/<slug>/compose.yaml` (generated, don't edit by hand):

- container `prime-agent-<slug>`: `sleep infinity` keep-alive, host network, the
  workspace RW-mounted at `/workspace`, its own state volume
  `prime-agent-<slug>-state` at `/home/agent/.prime/agent`, and the repo's
  `models.json` bind-mounted read-only on top;
- lifecycle via `podman compose -f <file>` (the docker-compose provider talking
  to the **rootless podman API socket** — `agent.sh` enables `podman.socket`
  for you on first use).

Legacy per-workspace **quadlet** units migrate automatically: if a
`prime-agent-<slug>.container` still exists in `~/.config/containers/systemd`,
re-registering (or removing) that slug retires the systemd unit and recreates
the same container and state volume under compose.

## Setup

```bash
# Build the image (podman/ is the build context; Dockerfile + models.json are there).
cd podman && ./build.sh
```

## Run

```bash
agent.sh <workspace-path> [slug]   # register + start (idempotent; migrates old quadlets)
agent.sh list                      # every registered workspace + live status
agent.sh exec <slug>               # enter the keep-alive container -> interactive TUI
agent.sh shell <slug>              # plain shell in the container
agent.sh status|start|stop|logs|ps <slug>
agent.sh remove <slug>             # stop + unregister + drop its state volume
```

The slug defaults to the lowercased workspace basename. Registering a second
workspace is just another `agent.sh <path>` call — N workspaces run side by
side, each with its own container and state volume.

Inside the TUI, pick the provider/model. The local provider is available as
`qwen-local` / model `Qwen3.8-27b`, pointed at `https://llm.linole.org/v1`.

## Changing the LLM / model

- **Edit the provider** — tweak `baseUrl` / `models` in
  [`podman/models.json`](podman/models.json); it is a live host bind, picked up on the
  next TUI start (no rebuild or restart needed).
- **Add auth** — the `qwen-local` provider references the `LOCAL_LLM_KEY` env var;
  the current gateway ignores it (set to `dummy`). If your backend starts requiring a
  key, set its real value in the compose template inside `agent.sh`
  (`LOCAL_LLM_KEY:`), then re-register the workspaces.

## Update the agent

```bash
cd podman && ./build.sh      # rebuild image (the installer re-fetches the latest)
agent.sh <path> <slug>       # re-register: recreates that workbench on the new image
```

## Logs & teardown

```bash
agent.sh logs <slug>     # container log tail (the TUI itself runs on your exec tty)
agent.sh remove <slug>   # stop + unregister + drop the container & state volume
```

> `remove` deletes the `prime-agent-<slug>-state` volume — i.e. agent sessions,
> `auth.json`, and the kernel venv. Use it only when you want a fresh agent.

## Migrating from the old quadlet layout

Existing quadlet registrations (`prime-agent-<slug>.container` in
`~/.config/containers/systemd`) keep running untouched until you choose to
migrate them. Re-registering that workspace retires the systemd unit and
recreates the identical container + state volume under compose:

```bash
agent.sh ~/projects/cloud        # quadlet unit removed, compose project takes over,
                                 # prime-agent-cloud-state volume (sessions) survives
```

`agent.sh list` prints a reminder line for every legacy quadlet still installed.

## Reboot behaviour (quadlet trade-off)

Compose projects are **not** wired into systemd, so unlike the old quadlet
units they do not come back after a host reboot by themselves (lingering is
no longer relevant). Just re-run `agent.sh <path>` per workspace — it is
idempotent and keeps all state. `restart: unless-stopped` still covers
container crashes while the machine is up.

## Notes / troubleshooting

- **First run provisions the IPython kernel.** Prime Agent provisions its RLM kernel
  into the state volume on the first interactive use. It is deliberately *not* baked
  into the image, so it persists across image rebuilds.
- **Rootless network is host.** The agent makes only outbound calls; no ports are
  published. If `https://llm.linole.org` is unreachable from the host, check host
  firewall/VPN before touching the container.
- **`podman compose` complains it cannot reach the API** — the compose provider
  talks to the rootless podman socket; `agent.sh` enables it, or do it manually:
  `systemctl --user enable --now podman.socket`.
- **`prime-agent` not found after rebuild** — the installer runs as root, so the
  binary lands in `/root/.local/bin` and only patches shell rc files; the
  Dockerfile fixes this with `ENV PATH="/root/.local/bin:${PATH}"` after the
  install step. Keep that line if the Dockerfile is restructured.
- **Workspace writes don't appear on host** — confirm the host path exists and the
  `rw` bind in the compose file points at it; `podman exec prime-agent-<slug> sh -c 'touch /workspace/.writetest'`.

## Out of scope

LXC `profile.yaml` (this deploy targets this machine, not a container), GPU
pass-through (the agent is CPU-only), and interactive-TUI automation (only how-to,
not wired).
