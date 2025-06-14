# etcd
https://etcd.io/docs/v3.6/quickstart/

## setup

### homebrew 
* /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
* test -d ~/.linuxbrew && eval "$(~/.linuxbrew/bin/brew shellenv)"
* test -d /home/linuxbrew/.linuxbrew && eval "$(/home/linuxbrew/.linuxbrew/bin/brew shellenv)"
* echo "eval \"\$($(brew --prefix)/bin/brew shellenv)\"" >> ~/.bashrc
* sudo apt-get install build-essential
* brew update
* brew install gcc
* brew install etcd
* sudo tee /etc/systemd/system/etcd.service > /dev/null <<'EOF'
[Unit]
Description=etcd key-value store
Documentation=https://github.com/etcd-io/etcd
After=network-online.target local-fs.target remote-fs.target time-sync.target
Wants=network-online.target local-fs.target remote-fs.target time-sync.target

[Service]
Type=notify
ExecStart=/bin/sh -c 'etcd'
Environment=ETCD_DATA_DIR=/var/lib/etcd/data
Environment=ETCD_WAL_DIR=/var/lib/etcd/wal
Environment=ETCD_NAME=etcd 
Restart=always
RestartSec=10s
LimitNOFILE=40000

[Install]
WantedBy=multi-user.target
EOF
* sudo systemctl daemon-reload
* sudo systemctl enable etcd
* sudo systemctl start etcd
* sudo systemctl status etcd


### manual
* cd /temp
* wget https://github.com/etcd-io/etcd/releases/download/v3.6.0/etcd-v3.6.0-linux-amd64.tar.gz
* tar -xvf etcd-v3.6.0-linux-amd64.tar.gz
* sudo mv etcd-v3.6.0-linux-amd64/etcd* /usr/local/bin/

## restore from backup
* etcdctl --endpoints=https://127.0.0.1:2379 
  snapshot restore s3://k3s.j8t7.ldn203.idrivee2-94.com/etcd-snapshot-master0-1749902402