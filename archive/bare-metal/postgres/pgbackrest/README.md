
# pgbackrest
* https://pgbackrest.org/user-guide.html#installation
* https://pgbackrest.org/user-guide.html#s3-support
* https://bun.uptrace.dev/postgres/pgbackrest-s3-backups.html
* https://thedbadmin.com/automate-postgresql-daily-database-backup-using-pgbackreast-and-bash/
* https://www.enterprisedb.com/docs/supported-open-source/pgbackrest/07-use_case_2/

## installation
* https://pgbackrest.org/user-guide.html#installation
* mkdir -p /tmp/build
* wget -q -O - \
  https://github.com/pgbackrest/pgbackrest/archive/release/2.52.1.tar.gz | \
  tar zx -C /tmp/build
* sudo apt-get install python3-distutils meson gcc libpq-dev libssl-dev libxml2-dev \
  pkg-config liblz4-dev libzstd-dev libbz2-dev libz-dev libyaml-dev libssh2-1-dev
* meson setup /tmp/build/pgbackrest /tmp/build/pgbackrest-release-2.52.1
* ninja -C /tmp/build/pgbackrest
* sudo cp /tmp/build/pgbackrest/src/pgbackrest /usr/bin

## configuration
* sudo mkdir -p /etc/pgbackrest
* sudo chown postgres:postgres /etc/pgbackrest
* in postgresql.conf:
  * archive_mode = on
  * archive_command = 'pgbackrest --stanza=main archive-push %p'

## commands
* sudo -u postgres pgbackrest --stanza=main --log-level-console=info stanza-create
* sudo -u postgres pgbackrest --stanza=main --log-level-console=info check
* sudo -u postgres pgbackrest --type=full --stanza=main backup

## crontab
* sudo su postgres
* crontab -e
* add contents of cron file
* sudo apt install postfix

## Monitoring
* sudo apt-get -y install check-pgbackrest
* sudo check_pgbackrest --stanza=main --service=retention --retention-full=1 --output=human --retention-age=24h --retention-age-to-full=7d