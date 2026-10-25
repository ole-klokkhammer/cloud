LXC := core:cloud
LXC_BIN ?= lxc
QUADLET_NAME := triton
QUADLET_DIR := etc/containers/systemd
CONFIG_DIR := /ssd/models/surveillance/triton/config
CONFIG_MODELS := yolo26x rtdetr-x

.PHONY: deploy configs restart start stop status logs remove

deploy: configs
	$(LXC_BIN) file push ./$(QUADLET_NAME).container $(LXC)/$(QUADLET_DIR)/$(QUADLET_NAME).container
	$(LXC_BIN) exec $(LXC) -- systemctl daemon-reload
	$(LXC_BIN) exec $(LXC) -- systemctl restart $(QUADLET_NAME)

configs:
	for m in $(CONFIG_MODELS); do \
	  $(LXC_BIN) exec $(LXC) -- mkdir -p $(CONFIG_DIR)/$$m/1; \
	  for f in model_repository/$$m/*.pbtxt; do \
	    $(LXC_BIN) file push $$f $(LXC)$(CONFIG_DIR)/$$m/$$(basename $$f); \
	  done; \
	done
	$(LXC_BIN) exec $(LXC) -- find $(CONFIG_DIR) -maxdepth 3

restart:
	$(LXC_BIN) exec $(LXC) -- systemctl restart $(QUADLET_NAME)

stop:
	$(LXC_BIN) exec $(LXC) -- systemctl stop $(QUADLET_NAME)

start:
	$(LXC_BIN) exec $(LXC) -- systemctl start $(QUADLET_NAME)

status:
	$(LXC_BIN) exec $(LXC) -- systemctl status $(QUADLET_NAME)

logs:
	$(LXC_BIN) exec $(LXC) -- journalctl -u $(QUADLET_NAME) -f

remove:
	$(LXC_BIN) exec $(LXC) -- systemctl stop $(QUADLET_NAME) || true
	$(LXC_BIN) exec $(LXC) -- systemctl disable $(QUADLET_NAME) || true
	$(LXC_BIN) file remove $(LXC)/$(QUADLET_DIR)/$(QUADLET_NAME).container
