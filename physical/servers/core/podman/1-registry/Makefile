HOST   := ubuntu@core
SYSTEMD_DIR := /etc/systemd/system
SYSTEMCTL_CMD := systemctl
REGISTRY_SERVICE := podman-registry-login.service

.PHONY: setup deploy deploy-registry status logs undeploy

deploy: deploy-registry

# needs /ssd/appdata/env/zot.env on the host (REGISTRY_URL/USERNAME/PASSWORD),
# readable by $(PUSER) - created manually, stays out of the repo:
#   sudo chgrp $(PUSER) /ssd/appdata/env/zot.env && sudo chmod 640
deploy-registry:
	scp $(REGISTRY_SERVICE) $(HOST):/tmp/
	ssh -t $(HOST) "\
        sudo mv /tmp/$(REGISTRY_SERVICE) $(SYSTEMD_DIR)/$(REGISTRY_SERVICE) && \
        sudo $(SYSTEMCTL_CMD) daemon-reload && \
        sudo $(SYSTEMCTL_CMD) enable --now $(REGISTRY_SERVICE) && \
        sudo $(SYSTEMCTL_CMD) status $(REGISTRY_SERVICE) --no-pager && \
        rm -f /tmp/$(REGISTRY_SERVICE)"

status:
	ssh -t $(HOST) "\
		sudo $(SYSTEMCTL_CMD) status $(REGISTRY_SERVICE) --no-pager; \
		sudo $(SYSTEMCTL_CMD) list-timers --no-pager | grep podman-gc || true; \
		sudo -u $(PUSER) podman --version || echo 'podman not set up for $(PUSER) yet - run make setup'"

logs:
	ssh -t $(HOST) "\
	sudo journalctl $(MACHINE_CMD) -u $(REGISTRY_SERVICE) -n 50 --no-pager"

undeploy:
	ssh -t $(HOST) "\
		sudo $(SYSTEMCTL_CMD) disable --now $(REGISTRY_SERVICE) || true; \
		sudo rm -f $(SYSTEMD_DIR)/$(REGISTRY_SERVICE); \
		sudo $(SYSTEMCTL_CMD) daemon-reload"
