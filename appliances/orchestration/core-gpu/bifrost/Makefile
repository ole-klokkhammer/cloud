CONTAINER := core:core-gpu
SERVICE   := bifrost.service
CONFIG    := config.json

.PHONY: deploy install restart status logs

deploy:
	lxc file push $(SERVICE) $(CONTAINER)/etc/systemd/system/$(SERVICE)
	lxc file push $(CONFIG) $(CONTAINER)/opt/bifrost/$(CONFIG)
	lxc exec $(CONTAINER) -- systemctl daemon-reload
	lxc exec $(CONTAINER) -- systemctl enable --now $(SERVICE)
	lxc exec $(CONTAINER) -- systemctl status $(SERVICE) --no-pager

install:
	lxc exec $(CONTAINER) -- bash -c "\
		apt-get update && apt-get install -y nodejs npm && \
		mkdir -p /opt/bifrost && \
		npm install -g @maximhq/bifrost"

restart:
	lxc exec $(CONTAINER) -- systemctl restart $(SERVICE)

status:
	lxc exec $(CONTAINER) -- systemctl status $(SERVICE) --no-pager

logs:
	lxc exec $(CONTAINER) -- journalctl -u $(SERVICE) -n 50 --no-pager
