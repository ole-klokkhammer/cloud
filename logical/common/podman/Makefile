# podman common Makefile - setup + registry login + GC for an LXC.
# fresh LXC: make setup && make deploy
LXC ?= core:seldon
UNIT_DIR := etc/systemd/system
REGISTRY_SERVICE := podman-registry-login.service
GC_SERVICE       := podman-gc.service
GC_TIMER         := podman-gc.timer

.PHONY: setup deploy deploy-registry deploy-gc gc-now status logs undeploy

deploy: deploy-registry deploy-gc

# bootstrap: podman + quadlet generator + auto-update timer + storage/registry checks.
# Idempotent; must NOT create /env/zot.env (secret, stays out of the repo).
setup:
	lxc file push podman-setup.sh $(LXC)/usr/local/bin/podman-setup.sh
	lxc exec $(LXC) -- chmod +x /usr/local/bin/podman-setup.sh
	lxc exec $(LXC) -- /usr/local/bin/podman-setup.sh

# needs /env/zot.env on the LXC (REGISTRY_URL/USERNAME/PASSWORD), created manually
deploy-registry:
	lxc file push $(REGISTRY_SERVICE) $(LXC)/$(UNIT_DIR)/$(REGISTRY_SERVICE)
	lxc exec $(LXC) -- systemctl daemon-reload
	lxc exec $(LXC) -- systemctl enable --now $(REGISTRY_SERVICE)
	lxc exec $(LXC) -- systemctl status $(REGISTRY_SERVICE) --no-pager

# daily GC: prune unused images (safe under quadlet AutoUpdate - re-pulled on start)
deploy-gc:
	lxc file push $(GC_SERVICE) $(LXC)/$(UNIT_DIR)/$(GC_SERVICE)
	lxc file push $(GC_TIMER) $(LXC)/$(UNIT_DIR)/$(GC_TIMER)
	lxc exec $(LXC) -- systemctl daemon-reload
	lxc exec $(LXC) -- systemctl enable --now $(GC_TIMER)


# one-shot run of what the timer does
gc-now:
	lxc exec $(LXC) -- sh -c 'podman image prune -af && podman system prune -af'

status:
	lxc exec $(LXC) -- systemctl status $(REGISTRY_SERVICE) $(GC_TIMER) --no-pager
	lxc exec $(LXC) -- systemctl list-timers --no-pager | grep podman-gc || true
	lxc exec $(LXC) -- test -f /env/zot.env || echo 'WARN: /env/zot.env missing - registry login will fail'

logs:
	lxc exec $(LXC) -- journalctl -u $(REGISTRY_SERVICE) $(GC_SERVICE) $(GC_TIMER) -n 50 --no-pager

undeploy:
	lxc exec $(LXC) -- systemctl disable --now $(GC_TIMER) $(REGISTRY_SERVICE) || true
	lxc exec $(LXC) -- rm -f /etc/systemd/system/$(REGISTRY_SERVICE) /etc/systemd/system/$(GC_SERVICE) /etc/systemd/system/$(GC_TIMER)
	lxc exec $(LXC) -- systemctl daemon-reload
