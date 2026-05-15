# postgres

## setup 
### storage
sudo zfs create db/postgres
sudo zfs set atime=off db/postgres
sudo zfs set compression=lz4 db/postgres
sudo zfs set recordsize=8K db/postgres   # 8K–16K; see note below
sudo zfs set logbias=latency db/postgres
sudo zfs set primarycache=all db/postgres
sudo zfs set secondarycache=all db/postgres

Notes:

recordsize:
Postgres page size is 8K. For pure DB-only datasets, recordsize=8K aligns best.
16K is a decent compromise if you might also have larger files or want fewer metadata ops.
Pick one and keep it; changing it later only affects newly written blocks.
compression=lz4 is almost always a win for DBs (light CPU, saves IO).
atime=off avoids extra writes on reads.

### lxc
- lxc profile create postgres
- lxc profile edit postgres
- lxc launch ubuntu:24.04 postgres -p default -p postgres
- lxc exec postgres -- bash


### timescaledb
https://docs.timescale.com/self-hosted/latest/install/installation-linux/#install-and-configure-timescaledb-on-postgresql


#### install postgres with correct data path
* apt install wget ca-certificates -y
wget -qO - https://www.postgresql.org/media/keys/ACCC4CF8.asc | sudo tee /etc/apt/trusted.gpg.d/pgdg.asc
echo "deb http://apt.postgresql.org/pub/repos/apt $(lsb_release -cs)-pgdg main" | \
  sudo tee /etc/apt/sources.list.d/pgdg.list
* sudo apt install postgresql-17 postgresql-common 
* sudo /usr/share/postgresql-common/pgdg/apt.postgresql.org.sh
* create appropriate data folders with permissions to postgres:postgres
  * sudo chown -R postgres:postgres /mnt/databases/postgresql/17/main
  * sudo chmod 700 /mnt/databases/postgresql/17/main
  * ensure root is accessible too sudo chmod 777 /mnt/databases 
* sudo pg_ctlcluster 17 main stop
* sudo pg_dropcluster 17 main
* sudo pg_createcluster 17 main --datadir=/mnt/databases/postgresql/17/main --start

#### add timescaledb
* sudo /usr/share/postgresql-common/pgdg/apt.postgresql.org.sh
* echo "deb https://packagecloud.io/timescale/timescaledb/ubuntu/ $(lsb_release -c -s) main" | sudo tee /etc/apt/sources.list.d/timescaledb.list
* wget --quiet -O - https://packagecloud.io/timescale/timescaledb/gpgkey | sudo gpg --dearmor -o /etc/apt/trusted.gpg.d/timescaledb.gpg
* sudo apt update
* if timescaledb isnt found:
  * sudo nano /etc/apt/sources.list.d/timescaledb.sources
  * change plucky to jammy
* sudo apt install timescaledb-2-postgresql-17 postgresql-client-17 
* update /etc/postgresql/17/main/postgresql.conf with: listen_addresses = '*'
* set /etc/postgresql/17/main/pg_hba.conf:
# Allow all users from local network with md5 password
host    all             all              0.0.0.0/0                       md5
host    all             all              ::/0                            md5

* sudo timescaledb-tune


#### pgvector embeddings
sudo apt update
sudo apt install postgresql-17-pgvector

CREATE EXTENSION IF NOT EXISTS vector;