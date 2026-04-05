CONTAINER := core:core-gpu
SERVICE   := bifrost.service

.PHONY: deploy install configure restart status logs remove-litellm

deploy:
	lxc file push $(SERVICE) $(CONTAINER)/etc/systemd/system/$(SERVICE)
	lxc file push config.json $(CONTAINER)/opt/bifrost/config.json
	lxc exec $(CONTAINER) -- systemctl daemon-reload
	lxc exec $(CONTAINER) -- systemctl enable --now $(SERVICE)
	lxc exec $(CONTAINER) -- systemctl status $(SERVICE) --no-pager

install:
	lxc exec $(CONTAINER) -- bash -c "\
		apt-get update && apt-get install -y nodejs npm && \
		mkdir -p /opt/bifrost"

# One-time: register llama.cpp as the 'llama-local' provider.
# Run after 'make deploy' once the service is up.
configure:
	lxc exec $(CONTAINER) -- bash -c "\
		curl -sf -X POST http://localhost:4000/api/v1/providers \
		  -H 'Content-Type: application/json' \
		  -d '{ \
		    \"name\": \"llama-local\", \
		    \"base_provider_type\": \"openai\", \
		    \"base_url\": \"http://localhost:8080/v1\", \
		    \"api_key\": \"sk-dummy\", \
		    \"capabilities\": {\"chat_completion\": true} \
		  }'"

restart:
	lxc exec $(CONTAINER) -- systemctl restart $(SERVICE)

status:
	lxc exec $(CONTAINER) -- systemctl status $(SERVICE) --no-pager

logs:
	lxc exec $(CONTAINER) -- journalctl -u $(SERVICE) -n 50 --no-pager

remove-litellm:
	lxc exec $(CONTAINER) -- systemctl stop litellm.service || true
	lxc exec $(CONTAINER) -- systemctl disable litellm.service || true
	lxc exec $(CONTAINER) -- rm -f /etc/systemd/system/litellm.service
	lxc exec $(CONTAINER) -- systemctl daemon-reload
	lxc exec $(CONTAINER) -- rm -rf /opt/litellm
