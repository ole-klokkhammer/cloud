# postgres

## setup
https://docs.timescale.com/self-hosted/latest/install/installation-linux/#install-and-configure-timescaledb-on-postgresql

### install postgres with correct data path
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

### add timescaledb
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

## pgbackrest
 
* sudo apt update
* sudo apt install pgbackrest
* update /etc/postgresql/17/main/postgresql.conf
archive_mode = on
archive_command = 'pgbackrest --stanza=main archive-push %p'
restore_command = 'pgbackrest --stanza=main archive-get %f %p'
archive_timeout = 1800s
* update /etc/pgbackrest/pgbackrest.conf. create it with postgres:postgres if not exists:
[global]
process-max=4
log-level-console=info
start-fast=y

repo1-type=s3
repo1-path=/
repo1-cipher-type=aes-256-cbc
repo1-cipher-pass=<postgres_s3_cipher>
repo-s3-verify-ssl=n
repo1-s3-uri-style=path
repo1-retention-diff=2
repo1-retention-full=2
repo1-s3-region=London-2
repo1-s3-bucket=postgres
repo1-s3-endpoint=j8t7.ldn203.idrivee2-94.com
repo1-s3-key=<s3_key>
repo1-s3-key-secret=<s3_secret>

[main]
pg1-port=5432
pg1-host-user=postgres
pg1-path=/var/lib/postgresql/17/main
pg1-socket-path=/var/run/postgresql

[global:archive-push]
compress-level=3


### restore from backup
* sudo systemctl stop postgresql
* sudo -u postgres pgbackrest --stanza=main --repo1-type=s3 restore
* sudo systemctl start postgresql