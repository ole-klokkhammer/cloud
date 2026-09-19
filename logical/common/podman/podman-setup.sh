#!/usr/bin/env bash
# podman-setup.sh - idempotent podman + quadlet bootstrap for an Ubuntu LXC.
#
# What it does (all steps re-runnable, safe on existing boxes):
#   1. prereq check (apt/systemd)
#   2. apt install: podman systemd-container (quadlet generator) gettext-base
#   3. enable podman-auto-update.timer (quadlets with AutoUpdate=true keep images fresh)
#   4. verify: quadlet generator present, storage driver sane (warn on vfs/zfs rootfs)
#   5. optional: registry.linole.org reachability (no login - no secrets in this script)
#
# Run inside the LXC as root:
#   lxc exec <lxc> -- /path/to/podman-setup.sh
# or pipe from the repo:
#   lxc exec <lxc> -- sh -c 'curl -fsSL <git>/logical/common/podman-setup.sh | bash'
#
# knobs (env):
#   PODMAN_EXTRA_PACKAGES  extra apt packages, space separated (default: none;
#                          e.g. 'podman-docker podman-compose')
#   REGISTRY_HOST          registry to reachability-check (default registry.linole.org)
#   SKIP_REGISTRY_CHECK=1  skip the registry check
#
# post-bootstrap (per-service): drop <svc>.container into /etc/containers/systemd/,
# then: systemctl daemon-reload && systemctl enable --now <svc>

set -euo pipefail

EXTRA="${PODMAN_EXTRA_PACKAGES:-}"
REGISTRY="${REGISTRY_HOST:-registry.linole.org}"

step() { printf '\n== %s ==\n' "$*"; }
warn() { printf 'WARN: %s\n' "$*" >&2; }

[ "$(id -u)" -eq 0 ] || { echo 'run as root (inside the LXC)' >&2; exit 1; }

step "prereqs"
command -v apt-get >/dev/null || { echo 'need apt (Ubuntu LXC)' >&2; exit 1; }
command -v systemctl >/dev/null || { echo 'need systemd' >&2; exit 1; }

step "apt install (podman + quadlet generator)"
if [ "${SKIP_APT_UPDATE:-0}" != 1 ]; then
  apt-get update
fi
# systemd-container = the systemd generator that turns .container quadlets into units
# gettext-base = podman's i18n dependency (same combo as the cameraagent README)
PKGS="podman systemd-container gettext-base $EXTRA"
# shellcheck disable=SC2086
apt-get install -y --no-install-recommends $PKGS

step "enable podman-auto-update.timer"
systemctl enable --now podman-auto-update.timer

step "verify quadlet generator"
if compgen -G '/usr/lib/systemd/system-generators/*podman*' >/dev/null \
   || compgen -G '/lib/systemd/system-generators/*podman*' >/dev/null; then
  echo "generator(s): $( (compgen -G '/usr/lib/systemd/system-generators/*podman*'; compgen -G '/lib/systemd/system-generators/*podman*') | tr '\n' ' ')"
else
  warn 'no podman systemd generator found - quadlets will NOT work; check systemd-container install'
fi
systemctl daemon-reload

step "verify storage driver"
DRV="$(podman info --format '{{.Store.GraphDriverName}}' 2>/dev/null || echo unknown)"
echo "storage driver: ${DRV}"
case "${DRV}" in
  vfs)
    warn 'vfs storage is slow + disk-heavy. On a ZFS-rootfs LXC: apt-get install fuse-overlayfs,
  then set storage driver fuse-overlayfs in /etc/containers/storage.conf (podman < 5.4 style)
  or [storage] driver="fuse-overlayfs" in containers.conf, and rm -rf /var/lib/containers/storage
  if the LXC has no images yet.'
    ;;
  overlay|fuse-overlayfs)
    echo 'storage driver OK'
    ;;
  *)
    warn "unexpected storage driver '${DRV}' - run: podman info"
    ;;
esac

if [ "${SKIP_REGISTRY_CHECK:-0}" = 1 ]; then
  step "registry check (skipped via SKIP_REGISTRY_CHECK)"
else
  step "registry reachability: ${REGISTRY}"
  CODE=""
  for SCHEME in https http; do
    CODE="$(curl -fsS -o /dev/null -m 5 -w '%{http_code}' "${SCHEME}://${REGISTRY}/v2/" 2>/dev/null || true)"
    case "${CODE}" in
      2*|4*) echo "reachable via ${SCHEME} (${CODE})"; break;;
    esac
  done
  case "${CODE}" in
    2*|4*) ;; # registry v2 answers 200 or 401 - both mean it's up
    *) warn "${REGISTRY} not reachable on https/http - check traefik/ufw before 'make image'" ;;
  esac
fi

step "done"
podman --version
echo "podman ready; quadlets go in /etc/containers/systemd/ (see each service's .container)"
echo "per-service deploy flow: make image && make deploy (per-service Makefile), then journalctl -u <svc> -f"
