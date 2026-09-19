LXC := core:cameraagent
LXC_BIN ?= lxc
IMAGE := registry.linole.org/detector:latest
# build context is the detector/ root (Dockerfile COPYs app/); this Makefile
# lives in podman/, so the context is one level up
BUILDDIR := ..
QUADLET_NAME := detector
QUADLET_DIR := etc/containers/systemd

.PHONY: image push deploy restart status logs

push-model:
	$(LXC_BIN) file push ../../*.onnx $(LXC)/models/

image:
	podman build -t $(IMAGE) -f Dockerfile $(BUILDDIR)

deploy:
	$(LXC_BIN) file push $(CURDIR)/$(QUADLET_NAME).container $(LXC)/$(QUADLET_DIR)/$(QUADLET_NAME).container
	$(LXC_BIN) exec $(LXC) -- systemctl daemon-reload
	$(LXC_BIN) exec $(LXC) -- systemctl restart $(QUADLET_NAME)

restart:
	$(LXC_BIN) exec $(LXC) -- systemctl restart $(QUADLET_NAME)

status:
	$(LXC_BIN) exec $(LXC) -- systemctl status $(QUADLET_NAME)

logs:
	$(LXC_BIN) exec $(LXC) -- journalctl -u $(QUADLET_NAME) -f
