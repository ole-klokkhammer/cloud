LXC := core:core-cloud
QUADLET_DIR := etc/containers/systemd

deploy-traefik:
	lxc file push traefik.container $(LXC)/$(QUADLET_DIR)/traefik.container
	lxc exec $(LXC) -- systemctl daemon-reload
	lxc exec $(LXC) -- systemctl restart traefik

status:
	lxc exec $(LXC) -- systemctl status traefik

logs:
	lxc exec $(LXC) -- journalctl -u traefik -f