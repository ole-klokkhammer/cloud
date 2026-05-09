REGISTRY := container-registry.home.lan:5000
IMAGE := matrix-ai-bot
TAG := latest

.PHONY: build push deploy clean

build:
	docker build -t $(REGISTRY)/$(IMAGE):$(TAG) .

push: build
	docker push $(REGISTRY)/$(IMAGE):$(TAG)

deploy: push
	nomad job run ai-bot.nomad.hcl

clean:
	docker rmi $(REGISTRY)/$(IMAGE):$(TAG) 2>/dev/null || true