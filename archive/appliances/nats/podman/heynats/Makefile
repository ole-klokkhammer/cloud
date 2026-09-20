\
LXC := core:nats
LXC_BIN ?= lxc
IMAGE := registry.linole.org/heynats:latest
QUADLET_NAME := heynats
SRC ?= $(CURDIR)/src/heynats

.PHONY: fetch build push build_and_deploy deploy enable restart stop status logs

deploy:
	$(LXC_BIN) file push ./$(QUADLET_NAME).container $(LXC)/etc/containers/systemd/$(QUADLET_NAME).container
	$(LXC_BIN) exec $(LXC) -- systemctl daemon-reload
	$(LXC_BIN) exec $(LXC) -- systemctl restart $(QUADLET_NAME)

enable:
	$(LXC_BIN) exec $(LXC) -- systemctl enable $(QUADLET_NAME)

restart:
	$(LXC_BIN) exec $(LXC) -- systemctl restart $(QUADLET_NAME)

stop:
	$(LXC_BIN) exec $(LXC) -- systemctl stop $(QUADLET_NAME)

status:
	$(LXC_BIN) exec $(LXC) -- systemctl status $(QUADLET_NAME)

logs:
	$(LXC_BIN) exec $(LXC) -- journalctl -u $(QUADLET_NAME) -f
