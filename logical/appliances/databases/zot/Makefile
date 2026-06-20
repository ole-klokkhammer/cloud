# Zot Container Registry Management Makefile
# This Makefile automates the deployment and management of the Zot appliance

CONTAINER := core:zot
SERVICE := zot.service
ZOT_VERSION := 2.1.17
ZOT_BINARY := /usr/bin/zot
ZOT_CONFIG_SRC := $(CURDIR)/config/config.json
ZOT_CONFIG_DEST := /etc/zot/config.json
ZOT_SERVICE_SRC := $(CURDIR)/config/$(SERVICE)
ZOT_SERVICE_DEST := /etc/systemd/system/$(SERVICE)

.PHONY: all install config service deploy status restart stop start uninstall

all: deploy

## Install Zot binary
install:
	@echo "Installing Zot v$(ZOT_VERSION)..."
	lxc exec $(CONTAINER) -- sudo apt update && sudo apt upgrade -y
	lxc exec $(CONTAINER) -- wget -O $(ZOT_BINARY) https://github.com/project-zot/zot/releases/download/v$(ZOT_VERSION)/zot-linux-amd64
	lxc exec $(CONTAINER) -- chmod +x $(ZOT_BINARY)
	lxc exec $(CONTAINER) -- chown root:root $(ZOT_BINARY)

## Deploy configuration file
config:
	@echo "Deploying Zot configuration..."
	lxc exec $(CONTAINER) -- mkdir -p /etc/zot
	lxc file push  $(ZOT_CONFIG_SRC) $(CONTAINER)/$(ZOT_CONFIG_DEST)

## Deploy systemd service unit
service:
	@echo "Deploying Zot systemd service..."
	lxc file push $(ZOT_SERVICE_SRC) $(CONTAINER)/$(ZOT_SERVICE_DEST)
	lxc exec $(CONTAINER) -- systemctl daemon-reload
	lxc exec $(CONTAINER) -- systemctl enable zot
	lxc exec $(CONTAINER) -- systemctl start zot

logs:
	lxc exec $(CONTAINER) -- journalctl -u $(SERVICE) -f

## Full deployment sequence
deploy: install config service
	@echo "Zot deployment completed successfully."

## Service management targets
status:
	lxc exec $(CONTAINER) -- systemctl status zot

restart:
	lxc exec $(CONTAINER) -- systemctl restart zot

stop:
	lxc exec $(CONTAINER) -- systemctl stop zot

start:
	lxc exec $(CONTAINER) -- systemctl start zot

## Clean up and remove Zot
uninstall:
	lxc exec $(CONTAINER) -- systemctl stop zot
	lxc exec $(CONTAINER) -- systemctl disable zot
	lxc exec $(CONTAINER) -- rm -f $(ZOT_SERVICE_DEST)
	lxc exec $(CONTAINER) -- rm -f $(ZOT_BINARY)
	lxc exec $(CONTAINER) -- rm -rf /etc/zot
	@echo "Zot uninstalled."