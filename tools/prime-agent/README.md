# prime-agent

Local **Prime Agent** [`PrimeIntellect-ai/prime-agent`](https://github.com/PrimeIntellect-ai/prime-agent)
appliance, run as **hardened rootless podman sandboxes** — one container per
workspace, created by [`agent.sh`](agent.sh). No compose, no systemd units.

Not a headless service: each sandbox is a keep-alive "workbench" container that
stays up, and you drop into it to drive the interactive coding TUI against a
mounted workspace.

```
/workspace                     <- your git repo (RW bind) -> the agent's CWD
/home/agent/.prime/agent       <- per-workspace named volume (sessions, auth, kernel venv)
podman/models.json             <- repo copy, bind-mounted :ro (source of truth)
/var/tmp                       <- bounded tmpfs (build scratch self-cleans)
```

## Files

| File | Purpose |
| :-- | :-- |
| [`agent.sh`](agent.sh) | Create/list/enter/remove sandboxes — plain `podman run`, no config dir |
| [`podman/Dockerfile`](podman/Dockerfile) | `node:24` image wrapping the official installer |
| [`podman/build.sh`](podman/build.sh) | Builds `prime-agent:latest` (context = `podman/`) |
| [`podman/models.json`](podman/models.json) | LLM provider config (`qwen-local`), bind-mounted live into every sandbox |

## Security posture

* **Isolated rootless network** (not host): no host-loopback or LAN access;
  outbound internet only, which is all the agent makes.
* **`no-new-privileges`** and **`--cap-drop ALL`**, re-adding only what apt/npm
  need (CHOWN, DAC_OVERRIDE, FOWNER, FSETID, KILL, SETGID, SETUID, SETPCAP, SYS_CHROOT).
* **`--pids-limit`** contains fork bombs and runaway builds.
* **`/var/tmp` is a bounded tmpfs** — buildah/podman build scratch dies with the
  container instead of leaking onto disk (this is what filled the SSD with 325G
  of `container_images_storage*` dirs once).
* **models.json bind-mounted `:ro`**; no host `$HOME` or dotfiles mounted.
* **Per-workspace state volume** isolates each sandbox's `auth.json`/sessions.
* The **workspace is mounted RW by design**: the repo is the trust boundary —
  anything the agent can do to the repo it will legitimately do.

## Setup

```bash
cd podman && ./build.sh        # build the image (models.json is NOT baked in)
```

## Run

```bash
agent.sh <workspace-path> [slug]   # create/refresh the sandbox (idempotent)
agent.sh list                      # all sandboxes + status
agent.sh exec <slug>               # enter the keep-alive container -> interactive TUI
agent.sh shell <slug>              # plain shell in the container
agent.sh logs <slug>               # container log tail (the TUI itself runs on your exec tty)
agent.sh start|stop <slug>
agent.sh remove <slug>             # delete the container (state volume kept)
agent.sh purge <slug>              # delete container AND state volume
```

The slug defaults to the lowercased workspace basename. Re-running `agent.sh
<path>` recreates the container on the current image with current flags — the
state volume (sessions, kernel venv) survives, so it doubles as the "update the
sandbox" step after `./build.sh`.

Inside the TUI, pick the provider/model: `qwen-local` / `llm` (and the older
`Qwen3.8-27b`), pointed at `https://llm.linole.org/v1`.

## Changing the LLM / model

- **Edit the provider** — tweak `baseUrl` / `models` in
  [`podman/models.json`](podman/models.json); it is a live host bind, picked up
  on the next TUI start (no rebuild or container restart needed). Caveat: a
  running daemon caches the model catalog, so fully exit prime-agent (or
  `agent.sh stop <slug> && agent.sh start <slug>`) after editing.
- **Add auth** — the `qwen-local` provider references the `LOCAL_LLM_KEY` env
  var; the current gateway ignores it (set to `dummy`). If your backend starts
  requiring a key, set its real value in `agent.sh` (`-e LOCAL_LLM_KEY=`) and
  re-register the workspaces. Or move it out of the file and pass it at run
  time.

## Update the agent

```bash
cd podman && ./build.sh      # rebuild image (the installer re-fetches the latest)
agent.sh <path> <slug>       # re-register: recreates the sandbox on the new image
```

## Reboot behaviour

Rootless podman does not restore containers on boot, so after a host reboot
re-run `agent.sh <path>` per workspace (idempotent, keeps all state).
`restart: unless-stopped` covers container crashes and podman restarts while
the machine is up. If auto-start on boot ever matters, the migration target is
a quadlet unit (systemd) per workspace — the flags translate 1:1; deliberately
not wired today.

## Notes / troubleshooting

- **First run provisions the IPython kernel** into the state volume; it is
  deliberately not baked into the image, so it survives rebuilds.
- **`prime-agent` not found after rebuild** — the installer runs as root, so
  the binary lands in `/root/.local/bin` and only patches shell rc files; the
  Dockerfile fixes this with `ENV PATH="/root/.local/bin:${PATH}"`. Keep that
  line if the Dockerfile is restructured.
- **Outbound calls fail from the sandbox** — the network is slirp4netns NAT;
  DNS and outbound TCP work by default. If `https://llm.linole.org` is
  unreachable from the host, fix the host (firewall/VPN) first.
- **Builds inside the sandbox hit the 8G /var/tmp cap** — raise `VARTMP_SIZE`
  in `agent.sh`; the cap exists to bound leak damage, not to be tight.

## Out of scope

GPU pass-through (the agent is CPU-only), interactive-TUI automation, quadlet
auto-start (deliberately deferred — see Reboot behaviour).
