# postgres

## setup
https://docs.timescale.com/self-hosted/latest/install/installation-linux/#install-and-configure-timescaledb-on-postgresql

* sudo apt-get install postgresql postgresql-common postgresql-contr
* sudo pg_createcluster <version> main --start
* sudo /usr/share/postgresql-common/pgdg/apt.postgresql.org.sh
* echo "deb https://packagecloud.io/timescale/timescaledb/ubuntu/ $(lsb_release -c -s) main" | sudo tee /etc/apt/sources.list.d/timescaledb.list
* wget --quiet -O - https://packagecloud.io/timescale/timescaledb/gpgkey | sudo gpg --dearmor -o /etc/apt/trusted.gpg.d/timescaledb.gpg
* sudo apt-get update
* sudo apt-get install timescaledb-2-postgresql-17 postgresql-client-17
* update postgresql.conf with: listen_addresses = '*'
* set /etc/postgresql/17/main/pg_hba.conf:
# Allow all users from local network with md5 password
host    all             all              0.0.0.0/0                       md5
host    all             all              ::/0                            md5

## pgbackrest

* sudo apt-get update
* sudo apt-get install pgbackrest
* update /etc/postgresql/17/main/postgresql.conf
archive_mode = on
archive_command = 'pgbackrest --stanza=main archive-push %p'
restore_command = 'pgbackrest --stanza=main archive-get %f %p'
archive_timeout = 1800s
* update /etc/pgbackrest/pgbackrest.conf
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