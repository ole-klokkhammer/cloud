# dashboard

## 
- lxc profile create lxd-dashboard
- lxc profile edit lxd-dashboard
- lxc launch ubuntu:24.04 lxd-dashboard -p default -p lxd-dashboard
- lxc exec lxd-dashboard -- bash
  - apt update && apt install wget nginx php-fpm php-curl sqlite3 php-sqlite3 -y 
  - find the newest release: https://github.com/lxdware/lxd-dashboard
    wget https://github.com/lxdware/lxd-dashboard/archive/v3.8.0.gz
    tar -xzf v3.8.0.gz
  - setup nginx
    cp -a lxd-dashboard-3.8.0/default /etc/nginx/sites-available/
    cp -a lxd-dashboard-3.8.0/lxd-dashboard /var/www/html/
    nano /etc/nginx/sites-enabled/default > ./config/nginx
  - setup data
    mkdir -p /var/lxdware/data/sqlite
    mkdir -p /var/lxdware/data/lxd
    mkdir -p /var/lxdware/backups
    chown -R www-data:www-data /var/lxdware/
    chown -R www-data:www-data /var/www/html
  - systemctl restart nginx

## connection with lxd
- on host
  - lxc config set core.https_address :8443
  - cd /tmp 
  - nano lxdware.crt (add cert from lxd dashboard)
  - lxc config trust add lxdware.crt
  - lxc config set core.https_address [::]