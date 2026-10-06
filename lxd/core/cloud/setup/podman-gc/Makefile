# podman common Makefile - setup + registry login + GC for an LXC.
# fresh LXC: make setup && make deploy
LXC ?= core:cloud
UNIT_DIR := etc/systemd/system
GC_SERVICE := podman-gc.service
GC_TIMER := podman-gc.timer

.PHONY: setup deploy deploy-registry deploy-gc gc-now status logs undeploy

# daily GC: prune unused images (safe under quadlet AutoUpdate - re-pulled on start)
deploy:
	lxc file push $(GC_TIMER) $(LXC)/$(UNIT_DIR)/$(GC_TIMER)
	lxc file push $(GC_SERVICE) $(LXC)/$(UNIT_DIR)/$(GC_SERVICE)
	lxc exec $(LXC) -- systemctl daemon-reload
	lxc exec $(LXC) -- systemctl enable --now $(GC_TIMER)

status:
	lxc exec $(LXC) -- systemctl list-timers --no-pager | grep podman-gc || true

logs:
	lxc exec $(LXC) -- journalctl -u $(GC_SERVICE) -n 50 --no-pager

undeploy:
	lxc exec $(LXC) -- systemctl disable --now $(GC_TIMER) $(GC_SERVICE)  || true
	lxc exec $(LXC) -- rm -f  /etc/systemd/system/$(GC_SERVICE) /etc/systemd/system/$(GC_TIMER)
	lxc exec $(LXC) -- systemctl daemon-reload
