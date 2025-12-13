# healthchecks

## zfs
sudo zfs create -o quota=4G ssd/appdata/healthchecks
sudo zfs set recordsize=16K ssd/appdata/healthchecks
sudo zfs set atime=off ssd/appdata/healthchecks
sudo zfs set logbias=latency ssd/appdata/healthchecks
sudo zfs set compression=lz4 ssd/appdata/healthchecks

## 
- lxc profile create healthchecks
- lxc profile edit healthchecks
- lxc launch ubuntu:24.04 healthchecks -p default -p healthchecks
- lxc exec healthchecks -- bash

- sudo apt update
sudo apt install -y python3-venv python3-pip git
sudo git clone https://github.com/healthchecks/healthchecks.git /opt/healthchecks
sudo chown -R www-data:www-data /opt/healthchecks
cd /opt/healthchecks
sudo -u www-data python3 -m venv .venv
sudo -u www-data bash -lc '. .venv/bin/activate && pip install -U pip wheel && pip install -r requirements.txt gunicorn'

- DEBUG=False
SECRET_KEY=$(openssl rand -hex 32)
ALLOWED_HOSTS=healthchecks.home.lan,localhost,127.0.0.1
DB=sqlite:////ssd/appdata/healthchecks/hc.sqlite
SITE_ROOT=http://healthchecks.home.lan
EMAIL_USE_VERIFICATION=False
TIME_ZONE=Europe/Oslo
- cd /opt/healthchecks
sudo -u www-data bash -lc '. .venv/bin/activate && ./manage.py migrate && ./manage.py createsuperuser && ./manage.py collectstatic --noinput'

- nano healthchecks.service
- sudo systemctl daemon-reload
sudo systemctl enable --now healthchecks
sudo systemctl status healthchecks