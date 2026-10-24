#!/usr/bin/env bash
#
# agent.sh — Prime Agent sandbox: one hardened rootless podman container per
#            workspace. No compose, no generator, no config dir.
#
#   agent.sh <workspace-path> [slug]   create/refresh prime-agent-<slug> (idempotent)
#   agent.sh exec|shell|logs|start|stop <slug>
#   agent.sh list                      all sandbox containers
#   agent.sh remove <slug>             delete container (state volume kept)
#   agent.sh purge <slug>              delete container AND its state volume
#
# Security posture (vs the old compose template):
#   * isolated rootless network (was: host) — no host-loopback or LAN access,
#     outbound internet only, which is all the agent needs
#   * no-new-privileges + capabilities dropped to the minimum apt/npm needs
#   * pids limit to contain fork bombs / runaway builds
#   * /var/tmp is a bounded tmpfs — buildah/podman build scratch self-cleans
#     on container restart instead of leaking onto disk
#   * models.json bind :ro; no host $HOME or dotfiles mounted
#   * workspace is rw by design: the repo is the trust boundary
#
# After a host reboot containers do not auto-start (rootless); re-run
# agent.sh <path> per workspace — idempotent, state volumes survive.

set -euo pipefail

IMAGE="prime-agent:latest"
APPLIANCE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MODEL_JSON="${APPLIANCE_DIR}/podman/models.json"
TZ_NAME="Europe/Oslo"
VARTMP_SIZE="8g"
PIDS_LIMIT=4096

die() { echo "agent.sh: error: $*" >&2; exit 1; }
sanitize() { echo "$1" | tr '[:upper:]' '[:lower:]' | sed -E 's/[^a-z0-9]+/-/g; s/^-+//; s/-+$//'; }
unit() { echo "prime-agent-$1"; }

register() {
    local ws="${1:?usage: agent.sh <workspace-path> [slug]}"
    local slug="${2:-$(sanitize "$(basename "$(realpath "$ws")")")}"
    local u vol
    ws="$(realpath "$ws")"
    [[ -d "$ws" ]] || die "workspace is not a directory: ${ws}"
    [[ -n "$slug" ]] || die "could not derive a slug from ${ws}"
    [[ -f "$MODEL_JSON" ]] || die "models.json not found at ${MODEL_JSON}"
    podman image exists "$IMAGE" >/dev/null 2>&1 || die "image ${IMAGE} missing: cd ${APPLIANCE_DIR}/podman && ./build.sh"

    u="$(unit "$slug")"; vol="${u}-state"
    podman run -d --replace --name "$u" --hostname "$u" \
        --restart unless-stopped \
        --working-dir /workspace \
        --security-opt no-new-privileges \
        --cap-drop ALL \
        --cap-add CHOWN --cap-add DAC_OVERRIDE --cap-add FOWNER --cap-add FSETID \
        --cap-add KILL --cap-add SETGID --cap-add SETUID --cap-add SETPCAP --cap-add SYS_CHROOT \
        --pids-limit "$PIDS_LIMIT" \
        --tmpfs /var/tmp:rw,nosuid,nodev,size="$VARTMP_SIZE" \
        -e PRIME_AGENT_CODING_AGENT_DIR=/home/agent/.prime/agent \
        -e LOCAL_LLM_KEY=dummy \
        -e TZ="$TZ_NAME" \
        -v "$ws":/workspace:rw \
        -v "$vol":/home/agent/.prime/agent \
        -v "$MODEL_JSON":/home/agent/.prime/agent/models.json:ro \
        "$IMAGE" sleep infinity

    echo "sandbox ${u} -> ${ws}"
    echo "  TUI          : agent.sh exec ${slug}"
    echo "  state volume : ${vol}"
}

remove() {
    local slug="${1:?usage: agent.sh remove <slug>}"
    podman rm -f "$(unit "$slug")" >/dev/null 2>&1 || true
    echo "removed $(unit "$slug") (state volume kept; 'purge' to drop it)"
}

purge() {
    local slug="${1:?usage: agent.sh purge <slug>}"
    remove "$slug"
    podman volume rm "$(unit "$slug")-state" >/dev/null 2>&1 || true
    echo "purged $(unit "$slug") including its state volume"
}

list() {
    podman ps -a --filter "name=^prime-agent-" \
        --format '{{.Names}}\t{{.Status}}\t{{.Image}}' || true
}

simple() {
    local slug="${1:?slug}"
    podman "${@:2}" "$(unit "$slug")"
}

case "${1:-list}" in
    remove) shift; remove "$@" ;;
    purge)  shift; purge "$@" ;;
    list)   list ;;
    exec)   shift; podman exec -it "$(unit "${1:?slug}")" prime-agent ;;
    shell)  shift; podman exec -it "$(unit "${1:?slug}")" sh ;;
    logs)   shift; podman logs -f --tail 40 "$(unit "${1:?slug}")" ;;
    start)  simple "${2:?}" start ;;
    stop)   simple "${2:?}" stop ;;
    -h|help) grep -E '^#( |$)' "$0" | sed -n '1,30p' ;;
    *) register "$1" "${2:-}" ;;
esac
