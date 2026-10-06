LXC := core:cloud
QUADLET_NAME := matrix.container
QUADLET_DIR := etc/containers/systemd

deploy:
	lxc file push $(QUADLET_NAME) $(LXC)/$(QUADLET_DIR)/$(QUADLET_NAME)
	lxc exec $(LXC) -- systemctl daemon-reload
	lxc exec $(LXC) -- systemctl restart matrix

status:
	lxc exec $(LXC) -- systemctl status matrix

logs:
	lxc exec $(LXC) -- journalctl -u matrix -f