CONTAINER := core:core-gpu
SERVICE   := litellm.service

.PHONY: deploy install restart status logs

deploy:
	lxc file push $(SERVICE) $(CONTAINER)/etc/systemd/system/$(SERVICE)
	lxc exec $(CONTAINER) -- systemctl daemon-reload
	lxc exec $(CONTAINER) -- systemctl enable --now $(SERVICE)
	lxc exec $(CONTAINER) -- systemctl status $(SERVICE) --no-pager

install:
	lxc exec $(CONTAINER) -- bash -c "\
		apt-get update && apt-get install -y python3-venv && \
		mkdir -p /opt/litellm && \
		python3 -m venv /opt/litellm/venv && \
		/opt/litellm/venv/bin/pip install 'litellm[proxy]'"

restart:
	lxc exec $(CONTAINER) -- systemctl restart $(SERVICE)

status:
	lxc exec $(CONTAINER) -- systemctl status $(SERVICE) --no-pager

logs:
	lxc exec $(CONTAINER) -- journalctl -u $(SERVICE) -n 50 --no-pager
