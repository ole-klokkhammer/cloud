LXC := core:frigate
QUADLET_NAME := frigate
QUADLET_DIR := etc/containers/systemd

.PHONY: deploy restart status logs

deploy:
	lxc file push $(QUADLET_NAME).container $(LXC)/$(QUADLET_DIR)/$(QUADLET_NAME).container
	lxc exec $(LXC) -- systemctl daemon-reload
	lxc exec $(LXC) -- systemctl restart $(QUADLET_NAME)

status:
	lxc exec $(LXC) -- systemctl status $(QUADLET_NAME)

restart:
	lxc exec $(LXC) -- systemctl restart $(QUADLET_NAME)

logs:
	lxc exec $(LXC) -- journalctl -u $(QUADLET_NAME) -f


	