# Bluetooth Bridge - Deploy to LXC
# Usage:
#   make deploy          - Full deploy (sync + install + restart)
#   make sync            - Just sync files
#   make restart         - Restart service
#   make logs            - Follow logs
#   make status          - Check service status

LXC_REMOTE ?= hub0
LXC_NAME ?= bluetooth
LXC_TARGET = $(LXC_REMOTE):$(LXC_NAME)
REMOTE_PATH = /opt/bluetooth-bridge
SERVICE_NAME = bluetooth-bridge

.PHONY: deploy sync install restart logs status setup

# Full deploy
deploy: sync install restart
	@echo "✅ Deployed to $(LXC_TARGET)"

# Sync source files
sync:
	@echo "📦 Syncing files to $(LXC_TARGET)..."
	lxc exec $(LXC_TARGET) -- mkdir -p $(REMOTE_PATH)
	lxc file push -r src/app/* $(LXC_TARGET)$(REMOTE_PATH)/
	lxc file push src/requirements.txt $(LXC_TARGET)$(REMOTE_PATH)/
	lxc file push .env.example $(LXC_TARGET)$(REMOTE_PATH)/

# Install dependencies (creates venv if needed)
install:
	@echo "📥 Installing dependencies..."
	lxc exec $(LXC_TARGET) -- bash -c '\
		cd $(REMOTE_PATH) && \
		if [ ! -f venv/bin/pip ]; then rm -rf venv && python3 -m venv venv; fi && \
		./venv/bin/pip install -q -r requirements.txt'

# First-time setup (run once)
setup:
	@echo "🔧 Setting up $(LXC_TARGET)..."
	lxc exec $(LXC_TARGET) -- apt update
	lxc exec $(LXC_TARGET) -- apt install -y python3 python3-venv
	lxc exec $(LXC_TARGET) -- mkdir -p $(REMOTE_PATH)
	lxc file push bluetooth-bridge.service $(LXC_TARGET)/etc/systemd/system/
	lxc exec $(LXC_TARGET) -- systemctl daemon-reload
	lxc exec $(LXC_TARGET) -- systemctl enable $(SERVICE_NAME)
	@echo "✅ Setup complete. Run 'make deploy' to deploy."

# Restart service
restart:
	@echo "🔄 Restarting service..."
	lxc exec $(LXC_TARGET) -- systemctl restart $(SERVICE_NAME)

# Stop service
stop:
	lxc exec $(LXC_TARGET) -- systemctl stop $(SERVICE_NAME)

# Follow logs
logs:
	lxc exec $(LXC_TARGET) -- journalctl -u $(SERVICE_NAME) -f

# Check status
status:
	lxc exec $(LXC_TARGET) -- systemctl status $(SERVICE_NAME)

# Shell into container
shell:
	lxc exec $(LXC_TARGET) -- bash
