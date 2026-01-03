# Bluetooth appliance - host & VM setup helpers
# Usage examples:
#   make host-setup      # Prepare host (disable bluetooth, install rfkill)
#   make vm-launch       # Launch bluetooth VM with profile
#   make vm-setup        # Install bluez and kernel extras inside VM
#   make vm-test         # Basic bluetoothctl test inside VM

LXC_REMOTE ?= hub0
LXC_NAME ?= bluetooth
LXC_IMAGE ?= ubuntu:24.04
LXC_PROFILE ?= bluetooth
LXC_TARGET = $(LXC_REMOTE):$(LXC_NAME)

.PHONY: host-setup host-kernel-disable vm-launch vm-setup vm-test

host-setup:
	@echo "[host] Disabling host bluetooth service and installing rfkill on $(LXC_REMOTE)..."
	lxc exec $(LXC_REMOTE): -- bash -c 'set -e; \
		sudo systemctl stop bluetooth || true; \
		sudo systemctl disable bluetooth || true; \
		sudo systemctl mask bluetooth || true; \
		sudo apt update; \
		sudo apt install -y rfkill; \
		sudo rfkill unblock bluetooth || true'

host-kernel-disable:
	@echo "[host] Blacklisting bluetooth kernel modules on $(LXC_REMOTE)..."
	lxc exec $(LXC_REMOTE): -- bash -c 'set -e; \
		sudo tee /etc/modprobe.d/blacklist-bluetooth.conf >/dev/null << "EOF"; \
		blacklist btusb; \
		blacklist btrtl; \
		blacklist btintel; \
		blacklist btbcm; \
		blacklist bluetooth; \
EOF
		sudo update-initramfs -u || true'
	@echo "[host] Bluetooth modules blacklisted. Reboot host $(LXC_REMOTE) manually to apply."

vm-launch:
	@echo "[host] Launching VM $(LXC_TARGET) with profile $(LXC_PROFILE) on $(LXC_REMOTE)..."
	lxc profile create $(LXC_REMOTE):$(LXC_PROFILE) || true
	@echo "Edit the bluetooth profile as needed, then run this target again if first time."
	lxc launch $(LXC_IMAGE) $(LXC_TARGET) --vm --profile $(LXC_PROFILE) || true
	lxc exec $(LXC_TARGET) -- bash || true

vm-setup:
	@echo "[vm] Installing bluez, usbutils and kernel extras in $(LXC_TARGET)..."
	lxc exec $(LXC_TARGET) -- bash -c 'apt update && apt upgrade -y && \
		apt install -y bluez usbutils linux-modules-extra-$$(uname -r) && \
		systemctl enable --now bluetooth'

vm-test:
	@echo "[vm] Testing bluetooth stack in $(LXC_TARGET)..."
	lxc exec $(LXC_TARGET) -- bash -c 'lsusb; hciconfig -a; bluetoothctl show'
