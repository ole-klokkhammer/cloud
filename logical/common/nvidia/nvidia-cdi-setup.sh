#!/usr/bin/env bash
# nvidia-cdi-setup.sh - idempotent NVIDIA Container Toolkit (CDI) bootstrap
# for a Proxmox LXC with PVE GPU passthrough (security.nesting=true).
#
# What it does (all steps re-runnable, safe on existing boxes):
#   1. prereq check (apt/systemd, /dev/nvidia* present)
#   2. NVIDIA apt repo (gpg key + signed-by list, distro-agnostic stable)
#   3. pinned apt install: nvidia-container-toolkit + base + libnvidia-container{,-tools}
#   4. enable nvidia-cdi-refresh.{path,service} (auto-regenerates the CDI spec
#      on host driver updates)
#   5. nvidia-ctk cdi generate -> /var/run/cdi/nvidia.yaml
#   6. smoke test: podman run --device nvidia.com/gpu=all <cuda image> nvidia-smi -L
#
# Run inside the LXC as root:
#   lxc exec <lxc> -- /path/to/nvidia-cdi-setup.sh
# or pipe from the repo:
#   lxc exec <lxc> -- sh -c 'curl -fsSL <git>/logical/common/nvidia-cdi-setup.sh | bash'
#
# knobs (env):
#   NVIDIA_CTK_VERSION  pinned toolkit version   (default 1.20.0-1, keep in sync fleet-wide)
#   CDI_OUTPUT          CDI spec path            (default /var/run/cdi/nvidia.yaml)
#   NVIDIA_TEST_IMAGE   smoke-test image         (default docker.io/nvidia/cuda:12.4.1-base-ubuntu22.04)
#   SKIP_NVIDIA_TEST=1  skip the podman smoke test
#   SKIP_APT_UPDATE=1   skip `apt-get update` (repo already cached)

set -euo pipefail

V="${NVIDIA_CTK_VERSION:-1.20.0-1}"
CDI_OUTPUT="${CDI_OUTPUT:-/var/run/cdi/nvidia.yaml}"
TEST_IMAGE="${NVIDIA_TEST_IMAGE:-docker.io/nvidia/cuda:12.4.1-base-ubuntu22.04}"

step() { printf '\n== %s ==\n' "$*"; }
warn() { printf 'WARN: %s\n' "$*" >&2; }

[ "$(id -u)" -eq 0 ] || { echo 'run as root (inside the LXC)' >&2; exit 1; }

step "prereqs"
command -v apt-get >/dev/null || { echo 'need apt (Ubuntu LXC)' >&2; exit 1; }
command -v systemctl >/dev/null || { echo 'need systemd' >&2; exit 1; }
if ls /dev/nvidia* >/dev/null 2>&1; then
  echo "GPU device(s): $(ls /dev/nvidia* 2>/dev/null | tr '\n' ' ')"
else
  warn 'no /dev/nvidia* - PVE GPU not attached? continuing (toolkit installs fine, CDI test will be limited)'
fi

step "apt prereqs (ca-certificates curl gnupg2)"
apt-get install -y --no-install-recommends ca-certificates curl gnupg2

step "NVIDIA apt repo (pinned stable)"
# idempotent: dearmor + overwrite of the list file are safe to repeat
curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey \
  | gpg --dearmor --yes -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg
curl -fsSL https://nvidia.github.io/libnvidia-container/stable/deb/nvidia-container-toolkit.list \
  -o /etc/apt/sources.list.d/nvidia-container-toolkit.list
# uncomment the experimental lines (same as the cameraagent README flow)
sed -i -e '/experimental/ s/^#//g' /etc/apt/sources.list.d/nvidia-container-toolkit.list

step "apt-get update + pinned install (v${V})"
if [ "${SKIP_APT_UPDATE:-0}" != 1 ]; then
  apt-get update
fi
apt-get install -y --no-install-recommends \
  nvidia-container-toolkit="${V}" \
  nvidia-container-toolkit-base="${V}" \
  libnvidia-container-tools="${V}" \
  libnvidia-container1="${V}"

step "enable cdi auto-refresh (host driver updates regenerate the spec)"
systemctl enable --now nvidia-cdi-refresh.path nvidia-cdi-refresh.service

step "generate CDI spec -> ${CDI_OUTPUT}"
mkdir -p "$(dirname "${CDI_OUTPUT}")"
nvidia-ctk cdi generate --output="${CDI_OUTPUT}"

step "verify"
grep -q 'nvidia.com/gpu' "${CDI_OUTPUT}" || { echo 'CDI spec missing nvidia.com/gpu entry' >&2; exit 1; }
echo "CDI spec OK: $(grep -c 'nvidia.com/gpu' "${CDI_OUTPUT}") gpu entrie(s)"

if [ "${SKIP_NVIDIA_TEST:-0}" = 1 ]; then
  step "smoke test (skipped via SKIP_NVIDIA_TEST)"
elif command -v podman >/dev/null; then
  step "smoke test: ${TEST_IMAGE} nvidia-smi -L"
  podman run --rm --device nvidia.com/gpu=all "${TEST_IMAGE}" nvidia-smi -L \
    && echo 'SMOKE TEST PASSED' \
    || warn 'smoke test failed - check PVE GPU passthrough + host driver, then re-run'
else
  warn 'podman not installed - skipping container smoke test'
fi


sudo nvidia-ctk cdi generate --output=/etc/cdi/nvidia.yaml
sudo systemctl enable --now nvidia-cdi-refresh.path
sudo systemctl enable --now nvidia-cdi-refresh.service

step "done"
echo "nvidia-container-toolkit ${V} ready in this LXC; CDI spec at ${CDI_OUTPUT}"
echo "quadlet/container: use AddDevice=nvidia.com/gpu=all (podman) or the CDI name"
