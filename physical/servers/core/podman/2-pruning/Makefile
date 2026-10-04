HOST   := ubuntu@core
SYSTEMD_DIR := /etc/systemd/system
SYSTEMCTL_CMD := systemctl
GC_SERVICE       := podman-gc.service
GC_TIMER         := podman-gc.timer

.PHONY: setup deploy deploy-gc status logs undeploy

deploy: deploy-gc

# daily GC: prune stale/dangling images only (never volumes - see podman-gc.service)
deploy-gc:
	scp $(GC_SERVICE) $(GC_TIMER) $(HOST):/tmp/
	ssh -t $(HOST) "\
		sudo mv /tmp/$(GC_SERVICE) $(SYSTEMD_DIR)/$(GC_SERVICE) && \
		sudo mv /tmp/$(GC_TIMER) $(SYSTEMD_DIR)/$(GC_TIMER) && \
		sudo $(SYSTEMCTL_CMD) daemon-reload && \
		sudo $(SYSTEMCTL_CMD) enable --now $(GC_TIMER) && \
		sudo rm -f /tmp/$(GC_SERVICE) /tmp/$(GC_TIMER)"

status:
	ssh -t $(HOST) "\
		sudo $(SYSTEMCTL_CMD) status $(GC_TIMER) --no-pager; \
		sudo $(SYSTEMCTL_CMD) list-timers --no-pager | grep podman-gc || true; \
		sudo -u $(PUSER) podman --version || echo 'podman not set up for $(PUSER) yet - run make setup'"

# timer units don't log under their own name (the .service they trigger does),
# and journalctl rejects "-u x.timer" with "Failed to add match: Invalid argument".
# Timer state comes from list-timers; its output lives under $(GC_SERVICE).
logs:
	ssh -t $(HOST) "\
		sudo journalctl -u $(GC_SERVICE) -n 50 --no-pager; \
		sudo $(SYSTEMCTL_CMD) list-timers --all --no-pager | grep $(GC_TIMER) || echo 'no $(GC_TIMER) found on host - run make deploy-gc'"

undeploy:
	ssh -t $(HOST) "\
		sudo systemctl $(SYSTEMCTL_CMD) disable --now $(GC_TIMER) || true; \
		sudo systemctl $(SYSTEMCTL_CMD) daemon-reload"
