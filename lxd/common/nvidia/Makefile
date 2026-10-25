# nvidia/Makefile
#
# Idempotent NVIDIA Container Toolkit (CDI) bootstrap, two layers:
#   host:  install-host.sh on core (sudo) - toolkit + auto-refreshed CDI
#          spec in /var/run/cdi, the default search path for all users
#   guest: per-LXC bootstrap below for GPU LXCs (security.nesting=true)
#
# Usage:
#   make host                                   # core host toolkit (needs passwordless sudo via ssh)
#   make setup                                  # full LXC bootstrap, in order
#   make LXC=core:cloud generate                # just (re)generate the CDI spec
#
# Knobs (make overrides, mirror the script's env):
#   LXC, LXC_BIN, CTK_VERSION, CDI_OUTPUT, CDI_DIR, SKIP_APT_UPDATE

LXC ?= core:cloud
CORE_SSH ?= core
LXC_BIN ?= lxc

CTK_VERSION    ?= 1.20.1-1
CDI_OUTPUT     ?= /var/run/cdi/nvidia.yaml
CDI_DIR        ?= $(dir $(CDI_OUTPUT))
SKIP_APT_UPDATE    ?= 0

EXECSH = $(LXC_BIN) exec $(LXC) -- sh -c

# full bootstrap, in order
.PHONY: host setup prereq apt_prereq repo install enable_cdi generate verify

# host layer: run the sudo'd bootstrap on the LXD host
host:
	ssh $(CORE_SSH) 'sudo -n bash -s' < install-host.sh

setup: prereq apt_prereq repo install enable_cdi generate verify

# apt + systemd present; confirm PVE GPU passthrough (all checks in-LXC)
prereq:
	@$(LXC_BIN) exec $(LXC) -- sh -c "command -v apt-get >/dev/null || { echo 'need apt (Ubuntu LXC)' >&2; exit 1; }"
	@$(LXC_BIN) exec $(LXC) -- sh -c "command -v systemctl >/dev/null || { echo 'need systemd' >&2; exit 1; }"
	@$(LXC_BIN) exec $(LXC) -- sh -c "ls /dev/nvidia* >/dev/null 2>&1 && echo \"GPU device(s): \" \$(ls /dev/nvidia*) || echo 'WARN: no /dev/nvidia* - GPU not attached to this LXC?'"

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
