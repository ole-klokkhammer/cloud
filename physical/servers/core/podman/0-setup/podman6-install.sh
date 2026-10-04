#!/bin/bash
# One-shot: host-side podman 6.1.3 from source -> /usr/local/bin/podman.
#
# Why: noble's apt tops out at podman 4.9.3, whose cdi lib (v0.6.2) cannot read
# the CDI spec nvidia-container-toolkit 1.20.1 writes (cdi v1.x YAML format:
# "cdiVersion: 0.7.0" + device-level additionalGIDs). podman 6.1.3 vendors
# cdi v1.1.0 and reads that spec natively - no sed pinning, no spec conversion.
# No official prebuilt *host* binaries exist for Linux anymore (releases ship
# only the podman-remote client), so this builds once. ~5 min, ~600MB.
#
# Result: /usr/local/bin/podman (6.1.3) shadows apt's /usr/bin/podman (4.9.3,
# kept as fallback). apt conmon/crun/netavark/passt are unchanged (all
# compatible with podman 6). The obsolete podman49 sed-pinning drop-in is
# removed (its sed never matched the v1.x spec key anyway).
#
# Conservative alternative: PODMAN_TAG=v5.5.2 GO_VERSION=go1.23.7 (also
# reads the spec via cdi v1.0.1).
#
# Usage on core:  sudo bash podman6-install.sh

set -euo pipefail

PODMAN_TAG=v6.1.3
GO_VERSION=go1.26.8
SRC=/opt/podman-build
BIN=/usr/local/bin/podman

[ "$(id -u)" = 0 ] || { echo "run as root: sudo bash $0" >&2; exit 1; }

# preflight: ~4GiB free for toolchain + build cache
free=$(df -B1 /opt | awk 'NR==2 {print $4}')
if [ "$free" -lt 4294967296 ]; then
    echo "need ~4GiB free on the /opt filesystem, have $((free / 1073741824))GiB" >&2
    exit 1
fi
command -v git >/dev/null || { echo "git is required" >&2; exit 1; }

step() { echo; echo "==> $*"; }

step "1/6 Go ${GO_VERSION} -> /usr/local/go (skipped if present)"
if [ ! -x /usr/local/go/bin/go ]; then
    curl -fsSL -o "/tmp/${GO_VERSION}.linux-amd64.tar.gz" \
        "https://go.dev/dl/${GO_VERSION}.linux-amd64.tar.gz"
    tar -C /usr/local -xzf "/tmp/${GO_VERSION}.linux-amd64.tar.gz"
    rm -f "/tmp/${GO_VERSION}.linux-amd64.tar.gz"
fi
export PATH=/usr/local/go/bin:$PATH
go version

step "2/6 podman ${PODMAN_TAG} source (vendored tree - no module downloads)"
rm -rf "${SRC}/src"
mkdir -p "${SRC}"
git clone --depth 1 -b "${PODMAN_TAG}" \
    https://github.com/podman-container-tools/podman "${SRC}/src"

step "3/6 build (CGO off, vendor/ tree - a few minutes)"
export GOCACHE="${SRC}/.gocache"
make -C "${SRC}/src" podman -j"$(nproc)"

step "4/6 install to ${BIN} (shadows apt's /usr/bin/podman on PATH)"
install -m 0755 "${SRC}/src/bin/podman" "${BIN}"
hash -r 2>/dev/null || true
podman --version

step "5/6 retire the obsolete podman49 sed-pinning drop-in"
DROPIN_DIR=/etc/systemd/system/nvidia-cdi-refresh.service.d
if [ -d "${DROPIN_DIR}" ]; then
    rm -f "${DROPIN_DIR}/podman49-compat.conf"
    rmdir "${DROPIN_DIR}" 2>/dev/null || true
    systemctl daemon-reload
    systemctl restart nvidia-cdi-refresh.service
fi
echo "spec now (nct-native v1.x format; podman 6.1.3 reads it):"
head -3 /var/run/cdi/nvidia.yaml

step "6/6 verify: rootless podman + NVIDIA CDI"
sudo -u podman podman --version
sudo -u podman podman run --rm --device nvidia.com/gpu=all \
    docker.io/library/ubuntu nvidia-smi -L

echo
echo "done. /usr/bin/podman (4.9.3, apt) remains as fallback."
