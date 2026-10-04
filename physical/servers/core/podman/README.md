# podman on core - rootful

Podman runs **rootful** (as root):

- storage: `/var/lib/containers`, config: `/etc/containers`
- default network: netavark "podman" bridge (podman0)
- quadlets, when used: `/etc/containers/systemd/*.container`

If an earlier rootless pass created a `podman` user, it is unused now; its
storage under `/home/podman/.local/share/containers` can be pruned once
you are sure nothing needs it.

## files

| file | role |
|---|---|
| `podman-setup.sh` | one-time bootstrap, run on the host as root; idempotent |
| `podman-gc.{service,timer}` | daily prune of root's storage |
| `podman-registry-login.service` | one-shot `podman login` from `/ssd/appdata/env/zot.env` |
| `Makefile` | dev-box entrypoints (scp + `ssh -t` pattern, see `../fans/Makefile`) |

## runbook (from the dev box)

```
make setup    # installs + runs podman-setup.sh as root:
              #   podman package, default bridge network,
              #   podman-auto-update.timer (if shipped), alpine smoke test
make deploy   # registry login + GC timer
make status / logs
```

Before `make deploy`: create `/ssd/appdata/env/zot.env` on core
(`REGISTRY_URL`, `REGISTRY_USERNAME`, `REGISTRY_PASSWORD`). No chgrp
needed - root reads it.

## running containers (on core)

```
sudo podman run -d --name x -p 8080:8080 registry.linole.org/<img>
```

- no XDG_RUNTIME_DIR / user-session juggling - the units run as root
- GPU workloads: nvidia-container-toolkit (CDI) applies per-container as before
- going back to rootless later means: a service user + subuid/subgid +
  XDG_RUNTIME_DIR + a pasta/slirp4netns network driver

## fallback: slirp4netns / pasta instead of bridge

```
sudo apt install slirp4netns    # or: passt
sudo podman network rm podman && sudo podman network create --driver slirp4netns podman
```
