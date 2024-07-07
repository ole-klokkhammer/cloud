## Rejoin master node
http://blog.sozinov.eu/2021/06/27/Replace-master-node-in-K3s.html


* kubectl delete node <node>
* /usr/local/bin/k3s-uninstall.sh
* copy certs etc from another master (server folder): sudo scp -r ./server/ ubuntu@192.168.10.203:/mnt/k3s/disk1/k3s
* Remove old database: sudo rm -R ./server/db ./server/db.old
* update symlink to token: /mnt/k3s/disk1/k3s/server$ ln -s /mnt/k3s/disk1/k3s/server/token /mnt/k3s/disk1/k3s/server/node-token
* if new folder, create symlinks? sudo ln -s /mnt/k3s/disk1/k3s/ /mnt/nvme0n1/
* curl -sfL https://get.k3s.io | K3S_TOKEN_FILE=~/.k3s/k3s-server-token K3S_URL=https://192.168.10.202:6443 INSTALL_K3S_EXEC="server --disable traefik --disable servicelb --write-kubeconfig-mode 644 --data-dir /mnt/k3s/disk1/k3s"  sh -
* Wait for 10 minutes and then drain new master as k3s should be stopped to return back startup script there.
* kubectl drain <node> --delete-local-data --ignore-daemonsets --force
* systemctl stop k3s
* remove uneccesary params: ExecStart=/usr/local/bin/k3s server --no-deploy servicelb --no-deploy traefik
* systemctl daemon-reload
* systemctl start k3s
* kubectl uncordon <node>