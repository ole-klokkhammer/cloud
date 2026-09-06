# anythingllm

https://docs.anythingllm.com/

## setup

### Disk
sudo zfs create -o compression=lz4 -o atime=off -o xattr=sa -o acltype=posixacl -o recordsize=1M ssd/appdata/anythingllm

### lxc 
lxc profile create anythingllm
lxc profile edit anythingllm
lxc launch ubuntu:24.04 anythingllm -p default -p anythingllm
lxc exec anythingllm -- bash

### install docker
sudo apt update
sudo apt install -y docker.io ca-certificates
sudo apt update
sudo apt install -y docker-compose-v2
sudo systemctl enable --now docker 


### postgres appliance
CREATE DATABASE anythingllm;
CREATE USER anythingllm WITH PASSWORD 'replace-me';
CREATE DATABASE anythingllm OWNER anythingllm;
GRANT ALL PRIVILEGES ON DATABASE anythingllm TO anythingllm;
CREATE EXTENSION IF NOT EXISTS vector;

###
copy in .env and docker-compose.yaml
sudo chown -R 1000:1000 /app/server/storage
docker compose up -d
docker compose logs -f