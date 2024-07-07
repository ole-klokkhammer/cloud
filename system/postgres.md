# basic setup for postgres
- sudo apt install postgresql postgresql-contrib
- sudo systemctl start postgresql.service
- set username and password: sudo -u postgres psql -c "ALTER USER postgres PASSWORD 'NewPassword';"
- allow other systems to access: listen_addresses = '*' in /etc/postgresql/12/main/postgresql.conf
- host all all 0.0.0.0/0 md5 in /etc/postgresql/12/main/pg_hba.conf


## certificates ?? 
* https://www.suse.com/c/rancher_blog/deploying_ha_k3s_external_database/