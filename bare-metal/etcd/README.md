# etcd
https://etcd.io/docs/v3.6/quickstart/

## setup

### manual - k3s needs a specific version
* cd /temp
* wget https://github.com/etcd-io/etcd/releases/download/v3.5.21/etcd-v3.5.21-linux-amd64.tar.gz
* tar -xvf etcd-v3.6.0-linux-amd64.tar.gz
* sudo mv etcd-v3.6.0-linux-amd64/etcd* /usr/local/bin/
* sudo tee /etc/systemd/system/etcd.service > /dev/null <<'EOF'
[Unit] 
Description=etcd key-value store
Documentation=https://github.com/etcd-io/etcd
After=network-online.target local-fs.target remote-fs.target time-sync.target
Wants=network-online.target local-fs.target remote-fs.target time-sync.target

[Service]
Type=notify
ExecStart=/usr/local/bin/etcd
Environment=ETCD_DATA_DIR=/var/lib/etcd/data
Environment=ETCD_WAL_DIR=/var/lib/etcd/wal
Environment=ETCD_NAME=etcd
Environment=ETCD_LISTEN_CLIENT_URLS=http://0.0.0.0:2379
Environment=ETCD_ADVERTISE_CLIENT_URLS=http://192.168.10.2:2379
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

## backup
* 

## restore from backup

### prereq
* curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
* unzip awscliv2.zip
* sudo ./aws/install
* aws configure
* aws s3 ls s3://k3s --endpoint-url https://j8t7.ldn203.idrivee2-94.com | tail -n 1
* aws s3 cp s3://k3s/etcd-snapshot-master0-1749902402  /tmp --endpoint-url https://j8t7.ldn203.idrivee2-94.com
* etcdctl snapshot restore /tmp/etcd-snapshot-master0-1749902402 --endpoints=https://127.0.0.1:2379 --data-dir /var/lib/etcd/data 

### do
* etcdctl --endpoints=https://127.0.0.1:2379 
  snapshot restore s3://k3s.j8t7.ldn203.idrivee2-94.com/etcd-snapshot-master0-1749902402


## ui client
etcd manager