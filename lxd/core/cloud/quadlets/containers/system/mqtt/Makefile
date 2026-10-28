# Fleet MQTT broker (NanoMQ 0.25) on the cloud LXC.
#
#   /etc/containers/systemd/mqtt.container      from mqtt.container
#   /ssd/appdata/mqtt/config/nanomq.conf        from config/nanomq.conf
#   /ssd/appdata/mqtt/data/                     SQLite: retained msgs + sessions
#   /ssd/appdata/env/nanomq.env                 API creds, created once, never overwritten
#
#   make deploy      state dirs + quadlet + config, restart
#   make config      push config only, restart
#   make restart
#   make status | logs
#   make uninstall   stop and remove the unit (state dirs kept)
#
# The container publishes nothing: the MQTT listener (1883) and the dashboard
# (8081) are on apps.network only, and traefik is the way in from outside - it
# publishes 1883 and routes TCP here. Deploy this BEFORE traefik, which cannot
# bind 1883 while the broker holds it.
#
# Run where the `lxc` CLI is configured for the `core:` remote, e.g.
#   make LXC_BIN='ssh core sudo lxc' deploy

LXC         := core:cloud
LXC_BIN     ?= lxc
SERVICE     := mqtt
QUADLET     := mqtt.container
QUADLET_DIR := /etc/containers/systemd
APPDATA     := /ssd/appdata/mqtt
CONF        := nanomq.conf

.PHONY: deploy config restart start stop status logs uninstall	

deploy:
	$(LXC_BIN) exec $(LXC) -- mkdir -p $(APPDATA)/config $(APPDATA)/data
	$(LXC_BIN) file push $(QUADLET) $(LXC)$(QUADLET_DIR)/$(QUADLET)
	$(LXC_BIN) file push config/$(CONF) $(LXC)$(APPDATA)/config/$(CONF)
	$(LXC_BIN) exec $(LXC) -- test -s $(APPDATA)/config/$(CONF)
	$(LXC_BIN) exec $(LXC) -- systemctl daemon-reload
	$(LXC_BIN) exec $(LXC) -- systemctl restart $(SERVICE)

config:
	$(LXC_BIN) file push config/$(CONF) $(LXC)$(APPDATA)/config/$(CONF)
	$(LXC_BIN) exec $(LXC) -- systemctl restart $(SERVICE)

restart:
	$(LXC_BIN) exec $(LXC) -- systemctl restart $(SERVICE)

start:
	$(LXC_BIN) exec $(LXC) -- systemctl start $(SERVICE)

stop:
	$(LXC_BIN) exec $(LXC) -- systemctl stop $(SERVICE)

status:
	$(LXC_BIN) exec $(LXC) -- systemctl status $(SERVICE) --no-pager

logs:
	$(LXC_BIN) exec $(LXC) -- journalctl -u $(SERVICE)  -f

uninstall:
	$(LXC_BIN) exec $(LXC) -- sh -c 'systemctl stop $(SERVICE); rm -f $(QUADLET_DIR)/$(QUADLET); systemctl daemon-reload'
