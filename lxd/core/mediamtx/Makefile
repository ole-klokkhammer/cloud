LXC := core:mediamtx
LXC_BIN ?= lxc
VERSION ?= 1.21.2
TARBALL := mediamtx_v$(VERSION)_linux_amd64.tar.gz
URL := https://github.com/bluenviron/mediamtx/releases/download/v$(VERSION)/$(TARBALL)
CACHE := /tmp/$(TARBALL)

.PHONY: install-binary deploy-unit start stop restart status logs

install-binary:
	test -f $(CACHE) || curl -fsSLo $(CACHE) $(URL)
	$(LXC_BIN) file push $(CACHE) $(LXC)/tmp/$(TARBALL)
	$(LXC_BIN) exec $(LXC) -- sh -c \
	  'cd /tmp && tar xzf $(TARBALL) mediamtx && install -m 0755 mediamtx /usr/local/bin/mediamtx && rm -f $(TARBALL)'
	$(LXC_BIN) exec $(LXC) -- mediamtx --version

deploy-unit:
	$(LXC_BIN) file push ./systemd/mediamtx.service $(LXC)/etc/systemd/system/mediamtx.service
	$(LXC_BIN) exec $(LXC) -- systemctl daemon-reload
	$(LXC_BIN) exec $(LXC) -- systemctl enable mediamtx

start:
	$(LXC_BIN) exec $(LXC) -- systemctl start mediamtx

stop:
	$(LXC_BIN) exec $(LXC) -- systemctl stop mediamtx

restart:
	$(LXC_BIN) exec $(LXC) -- systemctl restart mediamtx

status:
	$(LXC_BIN) exec $(LXC) -- systemctl status mediamtx --no-pager

logs:
	$(LXC_BIN) exec $(LXC) -- journalctl -u mediamtx -f
