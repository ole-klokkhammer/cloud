# CUDA python base image (shared by torch apps).
#
# Build ON THE LXC (needs docker.io for python:3.12-slim); push to the
# internal registry so cameraagent/etc. can FROM it on the LAN (no pfsense hop).
#
#   make build     
#   make push     

CONTAINER ?= core:cameraagent
LXC_BIN ?= lxc
IMAGE ?= registry.linole.org/py312:cu130

.PHONY: build push

build:
	podman build -t $(IMAGE) -f Dockerfile

push:
	podman push $(IMAGE)
