# basic setup for postgres
- sudo apt install postgresql postgresql-contrib
- sudo systemctl start postgresql.service
- set username and password: sudo -u postgres psql -c "ALTER USER postgres PASSWORD 'NewPassword';"
- allow other systems to access: listen_addresses = '*' in /etc/postgresql/12/main/postgresql.conf
- host all all 0.0.0.0/0 md5 in /etc/postgresql/12/main/pg_hba.conf


## certificates ?? 
* https://www.suse.com/c/rancher_blog/deploying_ha_k3s_external_database/

## access
* sudo -u postgres psql

# pgbackrest 
* https://pgbackrest.org/user-guide.html#s3-support
* https://bun.uptrace.dev/postgres/pgbackrest-s3-backups.html
* https://thedbadmin.com/automate-postgresql-daily-database-backup-using-pgbackreast-and-bash/
* https://www.enterprisedb.com/docs/supported-open-source/pgbackrest/07-use_case_2/
* sudo apt install pgbackrest
* mkdir -m 770 /var/log/pgbackrest
* chown postgres:postgres /var/log/pgbackrest
* mkdir /etc/pgbackrest
* set s3 credentials in ~/.bashrc
* copy pgbackrest conf to /etc/pgbackrest/pgbackrest.conf
* enable archive mode in /etc/postgresql/14/main/postgresql.conf
* sudo -u postgres pgbackrest --stanza=main --log-level-console=info stanza-create
* sudo -u postgres pgbackrest --stanza=main --log-level-console=info check
* sudo -u postgres pgbackrest --type=full --stanza=main backup

## commands
* sudo -u postgres pgbackrest --stanza=main --log-level-console=info check
* sudo -u postgres pgbackrest --type=full --stanza=main backup

## monitoring
* send email on failed cron job:
* MAILTO="foo@bar.com"
  0 5 * * * /bin/some_script > /dev/null 