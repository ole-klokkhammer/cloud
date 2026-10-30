# Fleet MQTT broker (mosquitto 2.0, Ubuntu 24.04) on its own LXC: core:mqtt.
#
#   /etc/systemd/system/mosquitto.service.d/fleet.conf   from systemd/fleet.conf
#   /ssd/appdata/mqtt/config/mosquitto.conf              from config/mosquitto.conf
#   /ssd/appdata/mqtt/mosquitto/mosquitto.db             retained msgs + QoS sessions
#
#   make install     apt install mosquitto + mosquitto-clients, restore the packaged unit
#   make upgrade     apt-get install --only-upgrade mosquitto mosquitto-clients
#   make deploy      state dirs + config + drop-in, daemon-reload, restart
#   make config      push config only (no restart)
#   make reload      push config, then SIGHUP
#   make restart | start | stop | status | logs
#   make test        publish + subscribe round trip, loopback and LAN
#   make save        force a persistence write now (SIGUSR1)
#   make uninstall   stop, disable, drop the unit override (state dirs kept)
#
# The broker listens on 1883 on every address of the instance. traefik, on core:cloud,
# publishes 1883 and routes its tcp service here - see
# ../cloud/quadlets/containers/system/traefik/dynamic/mqtt.yaml - so clients keep using
# cloud.homelan:1883 and nothing in the fleet changes when this moves.
#
# Config changes: mosquitto reloads most options on SIGHUP (`make config`), but listeners
# and persistence_location are not reloadable - those need `make restart`, which drops
# every client connection (they reconnect on their own).
#
# Run where the `lxc` CLI is configured for the `core:` remote, e.g.
#   make LXC_BIN='ssh core sudo lxc' deploy

LXC         := core:mqtt
LXC_BIN     ?= lxc
SERVICE     := mosquitto
PKG         := mosquitto mosquitto-clients

APPDATA     := /ssd/appdata/mqtt
CONF        := mosquitto.conf
CONF_DIR    := $(APPDATA)/config
STATE_DIR   := $(APPDATA)/mosquitto
DROPIN_DIR  := /etc/systemd/system/$(SERVICE).service.d
DROPIN      := fleet.conf
PORT        := 1883

# `lxc file push` needs the remote directory to exist, and mosquitto refuses to create
# its persistence directory, so both are made here and the owner set to the user the
# unit runs as (User=mosquitto in the drop-in).
.PHONY: install upgrade dirs config deploy restart start stop status logs test save uninstall

install:
	$(LXC_BIN) exec $(LXC) -- sh -c \
	  'DEBIAN_FRONTEND=noninteractive apt-get update -q && DEBIAN_FRONTEND=noninteractive apt-get install -y $(PKG)'
	$(MAKE) unit-restore
	$(LXC_BIN) exec $(LXC) -- mosquitto -h 2>&1 | head -2

upgrade:
	$(LXC_BIN) exec $(LXC) -- sh -c \
	  'DEBIAN_FRONTEND=noninteractive apt-get update -q && DEBIAN_FRONTEND=noninteractive apt-get install -y --only-upgrade $(PKG)'
	$(MAKE) unit-restore
	@echo "unit restored - run make deploy to re-apply the fleet drop-in"

# An apt upgrade overwrites /usr/lib/systemd/system/mosquitto.service, and on this
# instance it had also been edited by hand (ExecStart pointing at a path that does not
# exist). All differences from the package live in $(DROPIN_DIR)/$(DROPIN), so the
# packaged file is kept pristine.
unit-restore:
	$(LXC_BIN) exec $(LXC) -- sh -c \
	  'dpkg --verify mosquitto | grep -q systemd/system/mosquitto.service && DEBIAN_FRONTEND=noninteractive apt-get install -y --reinstall mosquitto || true'

dirs:
	$(LXC_BIN) exec $(LXC) -- mkdir -p $(CONF_DIR) $(STATE_DIR)
	$(LXC_BIN) exec $(LXC) -- chown -R mosquitto:mosquitto $(APPDATA)/mosquitto
	$(LXC_BIN) exec $(LXC) -- chmod 750 $(STATE_DIR)

config:
	$(LXC_BIN) file push config/$(CONF) $(LXC)$(CONF_DIR)/$(CONF)
	$(LXC_BIN) exec $(LXC) -- test -s $(CONF_DIR)/$(CONF)

deploy: dirs config
	# unlike a directory bind, `lxc file push` will not create the parent for you
	$(LXC_BIN) exec $(LXC) -- mkdir -p $(DROPIN_DIR)
	$(LXC_BIN) file push systemd/$(DROPIN) $(LXC)$(DROPIN_DIR)/$(DROPIN)
	$(LXC_BIN) exec $(LXC) -- systemctl daemon-reload
	$(LXC_BIN) exec $(LXC) -- systemctl enable $(SERVICE)
	$(LXC_BIN) exec $(LXC) -- systemctl restart $(SERVICE)
	$(LXC_BIN) exec $(LXC) -- systemctl is-active $(SERVICE)
	@echo "--- listener (want 0.0.0.0:$(PORT), not 127.0.0.1) ---"
	$(LXC_BIN) exec $(LXC) -- ss -ltn "( sport = :$(PORT) )"

reload: config
	$(LXC_BIN) exec $(LXC) -- systemctl reload $(SERVICE)
	@echo "--- reloaded; listeners and persistence_location need make restart ---"

restart:
	$(LXC_BIN) exec $(LXC) -- systemctl restart $(SERVICE)

start:
	$(LXC_BIN) exec $(LXC) -- systemctl start $(SERVICE)

stop:
	$(LXC_BIN) exec $(LXC) -- systemctl stop $(SERVICE)

status:
	$(LXC_BIN) exec $(LXC) -- systemctl status $(SERVICE) --no-pager

logs:
	$(LXC_BIN) exec $(LXC) -- journalctl -u $(SERVICE) -f

# Loopback proves the broker; the LAN address proves the listener is actually facing the
# network and not just localhost, which is the failure this setup had at first. -C 1
# exits after the first message, and the retained publish is the persistence check: run
# `make test` again after `make restart` and `up` still comes back.
test:
	$(LXC_BIN) exec $(LXC) -- sh -c \
	  'mosquitto_pub -h 127.0.0.1 -p $(PORT) -t fleet/check -m up -r && timeout 5 mosquitto_sub -h 127.0.0.1 -p $(PORT) -t fleet/check -C 1'
	IP=$$($(LXC_BIN) list $(LXC) --format csv -c 4 | cut -d' ' -f1); \
	$(LXC_BIN) exec $(LXC) -- sh -c \
	  "timeout 5 mosquitto_sub -h $$IP -p $(PORT) -t fleet/check -C 1"

save:
	$(LXC_BIN) exec $(LXC) -- systemctl kill -s USR1 $(SERVICE)

uninstall:
	$(LXC_BIN) exec $(LXC) -- sh -c \
	  'systemctl stop $(SERVICE); systemctl disable $(SERVICE); rm -f $(DROPIN_DIR)/$(DROPIN); rmdir $(DROPIN_DIR) 2>/dev/null; systemctl daemon-reload'
	@echo "kept: $(CONF_DIR)/$(CONF), $(STATE_DIR)"
