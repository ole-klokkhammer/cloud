HOST      := core
CONTAINER := torrent-stack
REMOTE    := $(HOST):$(CONTAINER)
SERVICE   := torrent-stack.service
PROFILE   := torrent-stack
STACK_DIR := /docker/torrent-stack
COMPOSE_FILE := $(STACK_DIR)/docker-compose.yaml
DOCKER_COMPOSE := docker compose -f $(COMPOSE_FILE)

WG_INTERFACE ?= wg0
WG_CONFIG    ?= /vpn/$(WG_INTERFACE).conf
LAN_SUBNET   ?= 192.168.10.0/24

.PHONY: all create configure deploy configure-vpn install-vpn \
	vpn-up vpn-down vpn-status vpn-killswitch-on vpn-killswitch-off \
	vpn-killswitch-test uninstall-nordvpn install-docker push start \
	restart stop status logs destroy shell

all: create configure deploy

configure: install-docker configure-vpn

# --- LXD Container Lifecycle ---

create:
	lxc profile create $(PROFILE) 2>/dev/null || true
	lxc profile edit $(PROFILE) < profile.yaml
	lxc launch ubuntu:24.04 $(CONTAINER) -p default -p $(PROFILE) --target $(HOST)
	@echo "Waiting for container to start..."
	@sleep 5
	lxc exec $(REMOTE) -- cloud-init status --wait 2>/dev/null || true

destroy:
	@echo "WARNING: This will destroy the $(CONTAINER) container and all its data."
	@read -p "Are you sure? [y/N] " confirm && [ "$$confirm" = "y" ] || exit 1
	lxc stop $(REMOTE) --force 2>/dev/null || true
	lxc delete $(REMOTE) 2>/dev/null || true

# --- WireGuard VPN ---

configure-vpn: install-vpn vpn-up vpn-status

install-vpn:
	@echo "Installing WireGuard tools..."
	lxc exec $(REMOTE) -- bash -lc "\
	apt-get update && \
	apt-get install -y wireguard-tools resolvconf curl"
	@echo "WireGuard installed."
	@echo "Place your WireGuard config at $(WG_CONFIG) inside the container."
	@echo "  e.g.: lxc file push wg0.conf $(REMOTE)$(WG_CONFIG)"

vpn-up:
	@echo "Bringing up WireGuard ($(WG_INTERFACE))..."
	lxc exec $(REMOTE) -- bash -lc '\
	wg-quick down $(WG_INTERFACE) 2>/dev/null || true; \
	[ -f "$(WG_CONFIG)" ] || { \
		echo "Config not found: $(WG_CONFIG)"; \
		exit 1; \
	}; \
	ln -sf "$(WG_CONFIG)" /etc/wireguard/$(WG_INTERFACE).conf && \
	chmod 600 /etc/wireguard/$(WG_INTERFACE).conf && \
	wg-quick up $(WG_INTERFACE) && \
	systemctl enable wg-quick@$(WG_INTERFACE)'
	@echo "WireGuard up and enabled on boot."

vpn-down:
	@echo "Bringing down WireGuard ($(WG_INTERFACE))..."
	lxc exec $(REMOTE) -- bash -lc '\
	wg-quick down $(WG_INTERFACE) 2>/dev/null || true; \
	systemctl disable wg-quick@$(WG_INTERFACE) 2>/dev/null || true'

vpn-killswitch-on:
	@echo "Enabling WireGuard kill switch..."
	lxc exec $(REMOTE) -- bash -lc '\
	endpoint=$$(grep -m1 "^Endpoint" /etc/wireguard/$(WG_INTERFACE).conf \
	  | sed "s/.*= *//;s/:.*//"); \
	iptables -F OUTPUT 2>/dev/null || true; \
	iptables -P OUTPUT DROP; \
	iptables -A OUTPUT -o lo -j ACCEPT; \
	iptables -A OUTPUT -o $(WG_INTERFACE) -j ACCEPT; \
	iptables -A OUTPUT -d $(LAN_SUBNET) -o eth0 -p udp --dport 53 -j DROP; \
	iptables -A OUTPUT -d $(LAN_SUBNET) -o eth0 -p tcp --dport 53 -j DROP; \
	iptables -A OUTPUT -d $(LAN_SUBNET) -o eth0 -j ACCEPT; \
	iptables -A OUTPUT -d "$$endpoint" -o eth0 -p udp -j ACCEPT; \
	ip6tables -F OUTPUT 2>/dev/null || true; \
	ip6tables -P OUTPUT DROP; \
	ip6tables -A OUTPUT -o lo -j ACCEPT; \
	ip6tables -A OUTPUT -o $(WG_INTERFACE) -j ACCEPT'
	@echo "Kill switch enabled. DNS blocked on LAN, only WireGuard traffic allowed."

vpn-killswitch-off:
	@echo "Disabling WireGuard kill switch..."
	lxc exec $(REMOTE) -- bash -lc '\
	iptables -P OUTPUT ACCEPT; \
	iptables -F OUTPUT 2>/dev/null || true; \
	ip6tables -P OUTPUT ACCEPT; \
	ip6tables -F OUTPUT 2>/dev/null || true'
	@echo "Kill switch disabled."

vpn-killswitch-test:
	@echo "=== Kill Switch Test ==="
	@lxc exec $(REMOTE) -- bash -lc '\
	fail=0; \
	echo "[1] OUTPUT policy..."; \
	policy=$$(iptables -S OUTPUT | head -1); \
	if echo "$$policy" | grep -q "DROP"; then \
	  echo "  PASS: OUTPUT policy is DROP"; \
	else \
	  echo "  FAIL: OUTPUT policy is not DROP ($$policy)"; fail=1; \
	fi; \
	echo ""; \
	echo "[2] IPv6 OUTPUT policy..."; \
	policy6=$$(ip6tables -S OUTPUT | head -1); \
	if echo "$$policy6" | grep -q "DROP"; then \
	  echo "  PASS: IPv6 OUTPUT policy is DROP"; \
	else \
	  echo "  FAIL: IPv6 OUTPUT policy is not DROP ($$policy6)"; fail=1; \
	fi; \
	echo ""; \
	echo "[3] DNS leak to LAN ($(LAN_SUBNET))..."; \
	if timeout 3 nslookup cloudflare.com 192.168.10.1 >/dev/null 2>&1; then \
	  echo "  FAIL: DNS resolved via LAN gateway (leak!)"; fail=1; \
	else \
	  echo "  PASS: DNS to LAN gateway blocked"; \
	fi; \
	echo ""; \
	echo "[4] DNS via VPN tunnel..."; \
	if timeout 5 nslookup cloudflare.com >/dev/null 2>&1; then \
	  echo "  PASS: DNS resolves through tunnel"; \
	else \
	  echo "  FAIL: DNS not working through tunnel"; fail=1; \
	fi; \
	echo ""; \
	echo "[5] Internet via VPN..."; \
	ip=$$(curl -4 -fsS --connect-timeout 5 --max-time 10 https://api.ipify.org 2>/dev/null); \
	if [ -n "$$ip" ]; then \
	  echo "  PASS: Public IP is $$ip"; \
	else \
	  echo "  FAIL: No internet through VPN"; fail=1; \
	fi; \
	echo ""; \
	echo "[6] Direct internet blocked (bypass test)..."; \
	if timeout 3 curl -4 -fsS --interface eth0 --connect-timeout 2 https://api.ipify.org >/dev/null 2>&1; then \
	  echo "  FAIL: Direct internet works outside VPN (leak!)"; fail=1; \
	else \
	  echo "  PASS: Direct internet blocked on eth0"; \
	fi; \
	echo ""; \
	if [ $$fail -eq 0 ]; then \
	  echo "=== ALL TESTS PASSED ==="; \
	else \
	  echo "=== SOME TESTS FAILED ==="; exit 1; \
	fi'

vpn-status:
	@echo "=== WireGuard ==="
	lxc exec $(REMOTE) -- bash -lc 'wg show $(WG_INTERFACE) 2>/dev/null || echo "$(WG_INTERFACE) not running"'
	@echo ""
	@echo "=== Public IP ==="
	@lxc exec $(REMOTE) -- bash -lc '\
	for url in \
	  https://api.ipify.org \
	  https://icanhazip.com \
	  https://ifconfig.me/ip \
	  https://ipinfo.io/ip; do \
	  ip=$$(curl -4 -fsS --connect-timeout 3 --max-time 8 "$$url" 2>/dev/null | tr -d "\r"); \
	  if [ -n "$$ip" ]; then \
	    echo "$$ip"; \
	    exit 0; \
	  fi; \
	done; \
	echo "Public IP lookup failed"' 
# --- Docker ---

install-docker:
	lxc exec $(REMOTE) -- bash -lc "\
	apt-get update && \
	apt-get install -y docker.io ca-certificates curl gnupg && \
	systemctl enable --now docker && \
	install -m 0755 -d /etc/apt/keyrings && \
	curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg && \
	echo \"deb [arch=\$$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \$$(lsb_release -cs) stable\" > /etc/apt/sources.list.d/docker.list && \
	apt-get update && \
	apt-get install -y docker-compose-plugin"

# --- Deployment ---

deploy: push start

push:
	lxc exec $(REMOTE) -- mkdir -p $(STACK_DIR)
	lxc file push docker/docker-compose.yaml $(REMOTE)$(COMPOSE_FILE)
	lxc file push docker/$(SERVICE) $(REMOTE)$(STACK_DIR)/$(SERVICE)

start:
	lxc file push docker/$(SERVICE) $(REMOTE)/etc/systemd/system/$(SERVICE)
	lxc exec $(REMOTE) -- systemctl daemon-reload
	lxc exec $(REMOTE) -- systemctl enable --now $(SERVICE)
	lxc exec $(REMOTE) -- systemctl status $(SERVICE) --no-pager

# --- Operations ---

restart:
	lxc exec $(REMOTE) -- systemctl restart $(SERVICE)

stop:
	lxc exec $(REMOTE) -- systemctl stop $(SERVICE)

status:
	@echo "=== Service ==="
	lxc exec $(REMOTE) -- systemctl status $(SERVICE) --no-pager || true
	@echo ""
	@echo "=== Containers ==="
	lxc exec $(REMOTE) -- $(DOCKER_COMPOSE) ps
	@echo ""
	@echo "=== WireGuard ==="
	lxc exec $(REMOTE) -- bash -lc 'wg show $(WG_INTERFACE) 2>/dev/null || echo "$(WG_INTERFACE) not running"'

logs:
	lxc exec $(REMOTE) -- $(DOCKER_COMPOSE) logs --tail=50

shell:
	lxc exec $(REMOTE) -- bash
