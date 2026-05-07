# redis
https://github.com/hivemq/hivemq-community-edition/wiki/Configuration

## setup

- lxc profile create redis
- lxc profile edit redis
- lxc launch ubuntu:24.04 redis -p default -p redis


## install redis
sudo apt update
sudo apt install -y redis-server

sudo systemctl enable --now redis-server
sudo systemctl status redis-server --no-pager -l


redis-cli -h 127.0.0.1 -p 6379 ping

## config?
sudo nano /etc/redis/redis.conf
sudo systemctl restart redis-server