# nvidia/Makefile
#
# Idempotent NVIDIA Container Toolkit (CDI) bootstrap for a Proxmox LXC with
# PVE GPU passthrough (security.nesting=true). Makefile mirror of
# nvidia-cdi-setup.sh, driven against a remote LXC in house style
# (see ../../linuxcontainers/surveillance/podman/triton/Makefile).
#
# Usage:
#   make setup                       # full bootstrap, in order
#   make LXC=core:cameraagent setup  # target a different LXC
#   make LXC=core:surveillance generate   # just (re)generate the CDI spec
#
# Knobs (make overrides, mirror the script's env):
#   LXC, LXC_BIN, CTK_VERSION, CDI_OUTPUT, CDI_DIR, SKIP_APT_UPDATE

LXC ?= core:surveillance
LXC_BIN ?= lxc

CTK_VERSION    ?= 1.20.1-1
CDI_OUTPUT     ?= /var/run/cdi/nvidia.yaml
CDI_DIR        ?= $(dir $(CDI_OUTPUT))
SKIP_APT_UPDATE    ?= 0

EXECSH = $(LXC_BIN) exec $(LXC) -- sh -c

# full bootstrap, in order
.PHONY: setup prereq apt_prereq repo install enable_cdi generate verify

setup: prereq apt_prereq repo install enable_cdi generate verify

# apt + systemd present; confirm PVE GPU passthrough (all checks in-LXC)
prereq:
	@$(LXC_BIN) exec $(LXC) -- sh -c "command -v apt-get >/dev/null || { echo 'need apt (Ubuntu LXC)' >&2; exit 1; }"
	@$(LXC_BIN) exec $(LXC) -- sh -c "command -v systemctl >/dev/null || { echo 'need systemd' >&2; exit 1; }"
	@$(LXC_BIN) exec $(LXC) -- sh -c "ls /dev/nvidia* >/dev/null 2>&1 && echo \"GPU device(s): \" \$(ls /dev/nvidia*) || echo 'WARN: no /dev/nvidia* - PVE GPU not attached?'"

# ca-certificates curl gnupg2
apt_prereq:
	$(EXECSH) "apt-get install -y --no-install-recommends ca-certificates curl gnupg2"

# NVIDIA apt repo (idempotent: dearmor+overwrite; uncomment experimental)
repo:
	$(EXECSH) "curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg && curl -fsSL https://nvidia.github.io/libnvidia-container/stable/deb/nvidia-container-toolkit.list -o /etc/apt/sources.list.d/nvidia-container-toolkit.list && sed -i -e '/experimental/ s/^#//g' /etc/apt/sources.list.d/nvidia-container-toolkit.list"

# pinned toolkit install (all four components on the same version)
install:
	$(EXECSH) "if [ \"$(SKIP_APT_UPDATE)\" != 1 ]; then apt-get update; fi; apt-get install -y --no-install-recommends nvidia-container-toolkit="$(CTK_VERSION)" nvidia-container-toolkit-base="$(CTK_VERSION)" libnvidia-container-tools="$(CTK_VERSION)" libnvidia-container1="$(CTK_VERSION)""

# enable CDI auto-refresh (regenerates the spec on host driver updates)
enable_cdi:
	$(EXECSH) "systemctl enable --now nvidia-cdi-refresh.path nvidia-cdi-refresh.service"

# generate the CDI spec
generate:
	$(EXECSH) "mkdir -p "$(CDI_DIR)" && nvidia-ctk cdi generate --output="$(CDI_OUTPUT)""

# verify the spec actually has gpu entries
verify:
	$(EXECSH) "grep -q 'nvidia.com/gpu' "$(CDI_OUTPUT)" || { echo 'CDI spec missing nvidia.com/gpu entry' >&2; exit 1; }; echo "CDI spec OK: $(CDI_OUTPUT)""
