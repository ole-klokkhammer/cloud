LXC := core:cameraagent
LXC_BIN ?= lxc
IMAGE := registry.linole.org/detector:latest
QUADLET_NAME := detector
QUADLET_DIR := etc/containers/systemd

.PHONY: push-model image deploy restart status logs

push-model:
	$(LXC_BIN) file push ./yolo11m.pt $(LXC):/models/yolo11m.pt

build_and_push:
	podman build -t $(IMAGE) -f Dockerfile .
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
