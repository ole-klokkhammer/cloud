# common

Shared pieces used by several LXCs — deploy with `make LXC=core:<name> ...`.

## podman (`podman/`)

The single source for every podman host (currently `cloud` and `llm`):
bootstrap script, zot registry login, and the GC timer.

```bash
make LXC=core:cloud setup && make LXC=core:cloud deploy
```

- **GC policy (do not "improve" it):** `podman image prune -f` only —
  dangling layers. Never `-a` and never `system prune`: "unused" images
  include temporarily-stopped apps, and unused volumes include data.
  (The previous common copy did exactly that; the fleet-safe version is
  from the cloud setup folder, June 2026.)
- Registry login needs `/env/zot.env` on the LXC (created manually,
  never in git).

## nvidia (`nvidia/`)

Two-layer bootstrap, one Makefile:

- `make host` — NVIDIA Container Toolkit on **core** (`install-host.sh`,
  passwordless sudo over ssh). Enables `nvidia-cdi-refresh` so the CDI spec
  in `/var/run/cdi` follows driver updates.
- `make LXC=core:<gpu-lxc> setup` — guest side: repo, pinned toolkit,
  in-guest CDI spec, verify has `nvidia.com/gpu` entries.
  Current GPU LXCs: cloud, llm.

## baseimages (`baseimages/`)

Dockerfiles for shared base images (python3.12+cuda) pushed to zot.
