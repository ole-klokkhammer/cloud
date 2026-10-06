LXC := core:cloud
QUADLET_NAME := traefik.container
QUADLET_DIR := etc/containers/systemd

deploy:
	lxc file push $(QUADLET_NAME) $(LXC)/$(QUADLET_DIR)/$(QUADLET_NAME)
	lxc exec $(LXC) -- systemctl daemon-reload
	lxc exec $(LXC) -- systemctl restart traefik

status:
	lxc exec $(LXC) -- systemctl status traefik

logs:
	lxc exec $(LXC) -- journalctl -u traefik -f