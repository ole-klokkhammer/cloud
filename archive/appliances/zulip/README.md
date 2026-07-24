# zulip

## setup

### Disk

sudo zfs create -o compression=lz4 -o atime=off -o xattr=sa -o acltype=posixacl ssd/appdata/zulip

### lxc

lxc profile create zulip
lxc profile edit zulip
lxc launch ubuntu:24.04 zulip -p default -p zulip
lxc exec zulip -- bash

### database

CREATE USER zulip WITH PASSWORD '<password>';
CREATE DATABASE zulip
WITH OWNER = zulip
ENCODING = 'UTF8'
LC_COLLATE = 'C.UTF-8'
LC_CTYPE = 'C.UTF-8'
TEMPLATE = template0;
GRANT ALL PRIVILEGES ON DATABASE zulip TO zulip;

## installation

```
cd $(mktemp -d)
curl -fLO https://download.zulip.com/server/zulip-server-latest.tar.gz
tar -xf zulip-server-latest.tar.gz

[ "$(whoami)" != "root" ] && sudo -s

./zulip-server-*/scripts/setup/install --push-notifications --self-signed-cert \
    --email=ole.klokkhammer@outlook.com --hostname=zulip.linole.org \
    --puppet-classes=zulip::profile::standalone_nodb,zulip::process_fts_updates \
    --postgresql-database-name=zulip \
    --postgresql-database-user=zulip \
    --postgresql-version=17
```

### Configuration

#### reverse proxy

https://zulip.readthedocs.io/en/stable/production/reverse-proxies.html

sudo nano /etc/zulip/zulip.conf:
[application_server]
http_only = true

[loadbalancer]
ips = 192.168.10.1

sudo /home/zulip/deployments/current/scripts/zulip-puppet-apply
sudo /home/zulip/deployments/current/scripts/restart-server

sudo nano /etc/zulip/settings.py
ZULIP_SERVICE_SUBMIT_USAGE_STATISTICS = False
ALLOWED_HOSTS = ['zulip.home.lan']

in pfsense frontend, enable to pass x-forwarded-for

#### postgres

sudo nano /etc/zulip/settings.py
REMOTE_POSTGRES_HOST = "postgres.linole.org"
REMOTE_POSTGRES_PORT = "5432"
REMOTE_POSTGRES_SSLMODE = "allow"

sudo nano /etc/zulip/zulip-secrets.conf
postgres_password = <zulip_postgres_password>

- Ask Zulip installer to initialize the PostgreSQL database.
  su zulip -c '/home/zulip/deployments/current/scripts/setup/initialize-database'

- And then generate a realm creation link:
  su zulip -c '/home/zulip/deployments/current/manage.py generate_realm_creation_link'

#### RabbitMQ Connection

on rabbitmq:
sudo rabbitmqctl add_user zulip "<password>"
sudo rabbitmqctl set_permissions -p / zulip "._" "._" ".\*"

on zulip:

```python
# In /etc/zulip/settings.py
RABBITMQ_HOST = 'rabbitmq.home.lan'
RABBITMQ_PORT = 5672
RABBITMQ_USERNAME = "zulip"
```

sudo nano /etc/zulip/zulip-secrets.conf
rabbitmq_password = <password>

#### redis

#### memcached?

#### uploads

can use s3

## logs

sudo tail -f /var/log/zulip/errors.log
