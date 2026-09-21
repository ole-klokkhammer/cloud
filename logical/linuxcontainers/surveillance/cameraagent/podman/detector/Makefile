LXC := core:cameraagent
LXC_BIN ?= lxc
IMAGE := registry.linole.org/surveillance/detector:latest
QUADLET_NAME := detector
QUADLET_DIR := etc/containers/systemd

MODELS_DIR ?= /ssd/llm/models/cameraagent
VENV ?= $(MODELS_DIR)/.venv

.PHONY: build_and_push deploy restart stop status logs

build_and_deploy: build push deploy

build:
	podman build -t $(IMAGE) -f Dockerfile .

push:
	podman push $(IMAGE)

deploy:
	$(LXC_BIN) file push ./$(QUADLET_NAME).container $(LXC)/etc/containers/systemd/$(QUADLET_NAME).container
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
