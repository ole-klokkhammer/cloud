# podman Makefile - setup + registry login + image GC on this host.
# Shape mirrors ../fans/Makefile: scp files to /tmp on the host, then a
# single ssh -t session installs them.
#
# podman runs ROOTFUL (as root): storage under /var/lib/containers,
# config under /etc/containers, default netavark network = bridge.
#
# fresh host:
#   make setup      # install + run podman-setup.sh as root
#   create /ssd/appdata/env/zot.env on the host (registry creds, out of the repo)
#   make deploy     # registry login + GC timer

HOST   := ubuntu@core
REGISTRY_SERVICE := podman-registry-login.service
GC_SERVICE       := podman-gc.service
GC_TIMER         := podman-gc.timer
SETUP_SCRIPT     := podman-setup.sh

.PHONY: setup deploy deploy-registry deploy-gc status logs undeploy

# install the bootstrap script on the host, then run it AS ROOT (rootful
# podman: storage/config live under /var/lib/containers + /etc/containers).
# Idempotent; must NOT create /ssd/appdata/env/zot.env (secret, stays out of the repo).
setup:
	scp $(SETUP_SCRIPT) $(HOST):/tmp/
	ssh -t $(HOST) "\
		sudo install -m 0755 /tmp/$(SETUP_SCRIPT) /usr/local/bin/$(SETUP_SCRIPT) && \
		sudo rm -f /tmp/$(SETUP_SCRIPT) && \
		sudo /usr/local/bin/$(SETUP_SCRIPT)"

deploy: deploy-registry deploy-gc

# needs /ssd/appdata/env/zot.env on the host (REGISTRY_URL/USERNAME/PASSWORD)
# - created manually, stays out of the repo.
deploy-registry:
	scp $(REGISTRY_SERVICE) $(HOST):/tmp/
	ssh -t $(HOST) "\
		sudo mv /tmp/$(REGISTRY_SERVICE) /etc/systemd/system/$(REGISTRY_SERVICE) && \
		sudo systemctl daemon-reload && \
		sudo systemctl enable --now $(REGISTRY_SERVICE) && \
		sudo systemctl status $(REGISTRY_SERVICE) --no-pager && \
		sudo rm -f /tmp/$(REGISTRY_SERVICE) && \
		(sudo test -f /ssd/appdata/env/zot.env && echo 'OK: /ssd/appdata/env/zot.env present') || echo 'WARN: /ssd/appdata/env/zot.env missing - registry login will fail'"

# daily GC: prune stale/dangling images only (never volumes - see podman-gc.service)
deploy-gc:
	scp $(GC_SERVICE) $(GC_TIMER) $(HOST):/tmp/
	ssh -t $(HOST) "\
		sudo mv /tmp/$(GC_SERVICE) /etc/systemd/system/$(GC_SERVICE) && \
		sudo mv /tmp/$(GC_TIMER) /etc/systemd/system/$(GC_TIMER) && \
		sudo systemctl daemon-reload && \
		sudo systemctl enable --now $(GC_TIMER) && \
		sudo rm -f /tmp/$(GC_SERVICE) /tmp/$(GC_TIMER)"

status:
	ssh -t $(HOST) "sudo systemctl status $(REGISTRY_SERVICE) $(GC_TIMER) --no-pager; \
		sudo systemctl list-timers --no-pager | grep podman-gc || true; \
		sudo podman --version || echo 'podman not installed yet - run make setup'"

logs:
	ssh -t $(HOST) "sudo journalctl -u $(REGISTRY_SERVICE) $(GC_SERVICE) $(GC_TIMER) -n 50 --no-pager"

undeploy:
	ssh -t $(HOST) "sudo systemctl disable --now $(GC_TIMER) $(REGISTRY_SERVICE) || true; \
		sudo rm -f /etc/systemd/system/$(REGISTRY_SERVICE) /etc/systemd/system/$(GC_SERVICE) /etc/systemd/system/$(GC_TIMER); \
		sudo systemctl daemon-reload"
