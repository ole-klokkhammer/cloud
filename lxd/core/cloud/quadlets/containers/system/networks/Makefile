LXC := core:cloud
QUADLET_NAME := apps.network
QUADLET_DIR := etc/containers/systemd

deploy:
	lxc file push $(QUADLET_NAME) $(LXC)/$(QUADLET_DIR)/$(QUADLET_NAME)
	lxc exec $(LXC) -- systemctl daemon-reload

status:
	lxc exec $(LXC) -- systemctl status apps.network

logs:
	lxc exec $(LXC) -- journalctl -u apps.network -f