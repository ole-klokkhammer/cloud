#!/usr/bin/env bash
# podman-setup.sh - bootstrap ROOTFUL podman on this host.
#
# Run as root (the Makefile does this via sudo):
#   sudo /usr/local/bin/podman-setup.sh
#
# Idempotent - safe to re-run. Rootful storage lives under
# /var/lib/containers, config under /etc/containers, and the default
# netavark network is the "podman" bridge (podman0). Quadlets, when used,
# live in /etc/containers/systemd/.

set -euo pipefail
export PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin

if [ "$(id -u)" != 0 ]; then
  echo "ERROR: run as root (sudo /usr/local/bin/podman-setup.sh)" >&2
  exit 1
fi

say() { printf '==> %s\n' "$*"; }

# 1. packages
if ! command -v podman >/dev/null; then
  say 'installing podman (apt)'
  apt-get update -qq
  apt-get install -y podman
fi

# 2. default network: bridge. If an earlier rootless pass left a
#    pasta/slirp4netns default, replace it.
cur=$(podman network inspect podman --format '{{.Driver}}' 2>/dev/null || echo absent)
if [ "$cur" = pasta ] || [ "$cur" = slirp4netns ]; then
  say "replacing non-bridge default network (${cur}) with bridge"
  podman network rm podman
fi
if ! podman network inspect podman >/dev/null 2>&1; then
  say "creating default bridge network 'podman'"
  podman network create --driver bridge podman
fi

# 3. quadlet auto-update timer (re-pulls images so quadlets track pinned
#    refs). Shipped with the podman package on some distros - guard for it.
if [ -f /lib/systemd/system/podman-auto-update.timer ] || [ -f /usr/lib/systemd/system/podman-auto-update.timer ]; then
  say 'enabling podman-auto-update.timer'
  systemctl daemon-reload
  systemctl enable --now podman-auto-update.timer
else
  echo 'NOTE: podman-auto-update.timer not shipped here - skipping (fine until quadlets are used)'
fi

# 4. smoke test
say 'smoke test: alpine on the default bridge'
podman run --rm docker.io/library/alpine:latest echo bridge-ok

say "done - $(podman --version)"
podman network ls
