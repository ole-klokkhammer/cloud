LXC := core:cameraagent
LXC_BIN ?= lxc
IMAGE := registry.linole.org/detector:latest
# LXC-local dir for build sources
BUILDDIR := .
QUADLET_NAME := detector
QUADLET_DIR := etc/containers/systemd

.PHONY: image push deploy restart status logs

push-model:
	$(LXC_BIN) file push ../yolo11m.onnx $(LXC)/models/yolo11m.onnx

image:
	podman build -t $(IMAGE) $(BUILDDIR)

deploy:
	$(LXC_BIN) file push $(QUADLET_NAME).container $(LXC)/$(QUADLET_DIR)/$(QUADLET_NAME).container
	$(LXC_BIN) exec $(LXC) -- systemctl daemon-reload
	$(LXC_BIN) exec $(LXC) -- systemctl restart $(QUADLET_NAME)

restart:
	$(LXC_BIN) exec $(LXC) -- systemctl restart $(QUADLET_NAME)

status:
	$(LXC_BIN) exec $(LXC) -- systemctl status $(QUADLET_NAME)

logs:
	$(LXC_BIN) exec $(LXC) -- journalctl -u $(QUADLET_NAME) -f
