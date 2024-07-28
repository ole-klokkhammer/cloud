# basic setup for postgres 
* https://www.postgresqltutorial.com/postgresql-getting-started/install-postgresql-linux/
- sudo apt update
- sudo apt install gnupg2 wget
- sudo sh -c 'echo "deb http://apt.postgresql.org/pub/repos/apt $(lsb_release -cs)-pgdg main" > /etc/apt/sources.list.d/pgdg.list'
- sudo apt install postgresql-16 postgresql-contrib-16
- sudo systemctl start postgresql.service
- sudo systemctl enable postgresql

## configuration
- set username and password: 
  - sudo -u postgres psql -c "ALTER USER postgres PASSWORD 'NewPassword';"
- allow other systems to access: 
  - listen_addresses = '*' in /etc/postgresql/16/main/postgresql.conf 
- sudo sed -i '/^host/s/ident/md5/' /etc/postgresql/16/main/pg_hba.conf
- sudo sed -i '/^local/s/peer/trust/' /etc/postgresql/16/main/pg_hba.conf
- echo "host all all 0.0.0.0/0 md5" | sudo tee -a /etc/postgresql/16/main/pg_hba.conf

## restore from backup
* sudo systemctl stop postgresql
* sudo -su postgres pgbackrest --stanza=main  restore

## upgrade
* sudo apt update
* sudo apt install postgresql-XX
* sudo systemctl stop postgresql
* status: pg_lsclusters
* sudo pg_dropcluster XX main --stop
* sudo -su postgres pg_upgradecluster YY main
* check that everything works
* pg_lsclusters
* sudo pg_dropcluster YY main --stop

## certificates ?? 
* https://www.suse.com/c/rancher_blog/deploying_ha_k3s_external_database/

## access
* sudo -u postgres psql


# logs 
- sudo tail -f /var/log/postgresql/postgresql-16-main.log
 

# uninstall
- dpkg -l | grep postgresql
- sudo apt-get --purge remove postgresql-16