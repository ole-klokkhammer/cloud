LXC := core:llm
LXC_BIN ?= lxc
IMAGE := registry.linole.org/infernix:latest
SRC := Infernix
QUADLET_NAME := infernix
QUADLET_DIR := etc/containers/systemd

.PHONY: update build push update_push build_and_deploy deploy restart stop status logs

update: ## refresh the Wallawalla47/Infernix source checkout
	git -C $(SRC) pull --ff-only

build: ## rebuild the image; --pull refreshes the nvidia/cuda base images
	podman build --pull -t $(IMAGE) -f $(SRC)/Dockerfile $(SRC)

push:
	podman push $(IMAGE)

update_push: update build push

build_and_deploy: update_push deploy

deploy:
	$(LXC_BIN) file push ./$(QUADLET_NAME).container $(LXC)/$(QUADLET_DIR)/$(QUADLET_NAME).container
	$(LXC_BIN) exec $(LXC) -- systemctl daemon-reload
	$(LXC_BIN) exec $(LXC) -- systemctl restart $(QUADLET_NAME)

restart:
	$(LXC_BIN) exec $(LXC) -- systemctl restart $(QUADLET_NAME)

stop:
	$(LXC_BIN) exec $(LXC) -- systemctl stop $(QUADLET_NAME)

status:
	$(LXC_BIN) exec $(LXC) -- systemctl status $(QUADLET_NAME)

logs:
	$(LXC_BIN) exec $(LXC) -- journalctl -u $(QUADLET_NAME) -f


	