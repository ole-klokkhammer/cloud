LXC := core:cloud
QUADLET_NAME := traefik.container
QUADLET_DIR := etc/containers/systemd
TRAEFIK_DYNAMIC_DIR := ssd/appdata/traefik/dynamic

deploy:
	lxc file push $(QUADLET_NAME) $(LXC)/$(QUADLET_DIR)/$(QUADLET_NAME)
	lxc exec $(LXC) -- systemctl daemon-reload
	lxc exec $(LXC) -- systemctl restart traefik

sync:
	# trailing slash is required: with several sources, `lxc file push` only treats
	# the target as a directory when the path ends in /
	lxc file push dynamic/* $(LXC)/$(TRAEFIK_DYNAMIC_DIR)/
	lxc exec $(LXC) -- systemctl daemon-reload
	lxc exec $(LXC) -- systemctl restart traefik

status:
	lxc exec $(LXC) -- systemctl status traefik

logs:
	lxc exec $(LXC) -- journalctl -u traefik -f