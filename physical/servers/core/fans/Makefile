HOST := ubuntu@core

.PHONY: deploy restart status logs

deploy:
	scp fan-control.sh fan-speed.service fan-speed.timer $(HOST):/tmp/
	ssh -t $(HOST) "\
		sudo mv /tmp/fan-control.sh /usr/local/bin/fan-control.sh && \
		sudo chmod +x /usr/local/bin/fan-control.sh && \
		sudo mv /tmp/fan-speed.service /etc/systemd/system/fan-speed.service && \
		sudo mv /tmp/fan-speed.timer /etc/systemd/system/fan-speed.timer && \
		sudo systemctl daemon-reload && \
		sudo systemctl enable --now fan-speed.timer && \
		sudo systemctl start fan-speed.service && \
		sudo systemctl status fan-speed.timer --no-pager"

restart:
	ssh -t $(HOST) "sudo systemctl start fan-speed.service"

status:
	ssh -t $(HOST) "sudo systemctl status fan-speed.timer --no-pager && echo '---' && sudo systemctl status fan-speed.service --no-pager"

logs:
	ssh -t $(HOST) "sudo journalctl -u fan-speed -n 20 --no-pager"
