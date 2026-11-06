LXC := core:cloud
LXC_BIN ?= lxc
NAME := opencode
IMAGE := registry.linole.org/system/opencode:latest
QUADLET_NAME := $(NAME).container
QUADLET_DIR := etc/containers/systemd
# Host folders backing the container mounts (see the Volume= lines).
APPDATA := /root/workspace/$(NAME)

# Bumped deliberately, never by a rebuild. `make build OPENCODE_VERSION=latest`
# to ride the edge. Must match the Dockerfile ARG default when you change it.
OPENCODE_VERSION ?= 1.19.5

.PHONY: build push build_and_deploy deploy restart stop status logs logs-app

build_and_deploy: build push deploy

build:
	podman build --build-arg OPENCODE_VERSION=$(OPENCODE_VERSION) -t $(IMAGE) -f Dockerfile .

push:
	podman push $(IMAGE)


deploy:
	$(LXC_BIN) exec $(LXC) -- mkdir -p $(APPDATA)/config $(APPDATA)/home/.local/share/opencode $(APPDATA)/workspace
	$(LXC_BIN) file push ./opencode.json $(LXC)$(APPDATA)/config/opencode.json
	# Providers count as connected only via auth.json (what /connect writes) or
	# a name listed in the provider's "env" being set on the server process.
	$(LXC_BIN) file push ./auth.json $(LXC)$(APPDATA)/home/.local/share/opencode/auth.json
	$(LXC_BIN) exec $(LXC) -- chown -R 1000:1000 $(APPDATA)
	$(LXC_BIN) file push $(QUADLET_NAME) $(LXC)/$(QUADLET_DIR)/$(QUADLET_NAME)
	$(LXC_BIN) exec $(LXC) -- systemctl daemon-reload
	$(LXC_BIN) exec $(LXC) -- systemctl restart $(NAME)

restart:
	$(LXC_BIN) exec $(LXC) -- systemctl restart $(NAME)

stop:
	$(LXC_BIN) exec $(LXC) -- systemctl stop $(NAME)

status:
	$(LXC_BIN) exec $(LXC) -- systemctl status $(NAME)

logs:
	$(LXC_BIN) exec $(LXC) -- journalctl -u $(NAME) -f

# opencode's request/runtime logging goes to a file in $HOME, not stdout; the
# journal only ever gets fatal crashes. Grep this for the ref=err_... ids the
# web UI surfaces on 500s.
logs-app:
	$(LXC_BIN) exec $(LXC) -- tail -f $(APPDATA)/home/.local/share/opencode/log/opencode.log
