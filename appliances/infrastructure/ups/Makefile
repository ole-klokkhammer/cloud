HOST := ubuntu@core

.PHONY: install deploy restart status logs test-shutdown

install:
	ssh -t $(HOST) "sudo apt-get update && sudo apt-get install -y apcupsd"

deploy:
	scp apcupsd.conf $(HOST):/tmp/apcupsd.conf
	ssh -t $(HOST) "\
		sudo mv /tmp/apcupsd.conf /etc/apcupsd/apcupsd.conf && \
		sudo rm -rf /etc/systemd/system/apcupsd.service.d && \
		sudo sed -i 's/^ISCONFIGURED=no/ISCONFIGURED=yes/' /etc/default/apcupsd && \
		sudo systemctl daemon-reload && \
		sudo systemctl restart apcupsd && \
		sudo systemctl status apcupsd --no-pager"

restart:
	ssh -t $(HOST) "sudo systemctl restart apcupsd"

status:
	ssh -t $(HOST) "apcaccess status"

logs:
	ssh -t $(HOST) "sudo journalctl -u apcupsd -n 50 --no-pager"

# Interactive UPS test utility (stop apcupsd first).
# WARNING: some menu options (e.g. kill power) WILL cut power.
test:
	ssh -t $(HOST) "sudo systemctl stop apcupsd && sudo apctest; sudo systemctl start apcupsd"
