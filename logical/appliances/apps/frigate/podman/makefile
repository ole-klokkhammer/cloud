# Variables
APP_NAME := frigate
LXC := core:frigate
CONFIG_DIR := /etc/containers/systemd
QUADLET_FILE := $(CONFIG_DIR)/$(APP_NAME).container

# Colors for output
C := \033[0;32m
R := \033[0;31m
NC := \033[0m

.PHONY: all deploy status logs restart shell

all: deploy

deploy:
	@echo "$(C)🚀 Deploying Frigate Quadlet...$(NC)"
	lxc exec $(LXC) -- mkdir -p $(CONFIG_DIR)
	lxc file push $(APP_NAME).container $(LXC)/$(QUADLET_FILE)
	lxc exec $(LXC) -- systemctl daemon-reload
	lxc exec $(LXC) -- systemctl restart $(APP_NAME)
	@echo "$(C)✅ Frigate is now running as a systemd service!$(NC)"

status:
	@echo "$(C)📊 Frigate Status:$(NC)"
	lxc exec $(LXC) -- systemctl status $(APP_NAME)
	lxc exec $(LXC) -- podman ps --filter name=$(APP_NAME)

logs:
	lxc exec $(LXC) -- journalctl -u $(APP_NAME) -f

restart:
	@echo "$(C)🔄 Restarting Frigate...$(NC)"
	lxc exec $(LXC) -- systemctl restart $(APP_NAME)

