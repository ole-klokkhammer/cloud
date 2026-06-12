# mattermost

https://docs.mattermost.com/deployment-guide/server/deploy-linux.html

## setup

### Disk

sudo zfs create -o compression=lz4 -o atime=off -o xattr=sa -o acltype=posixacl ssd/appdata/mattermost

### lxc

lxc profile create mattermost
lxc profile edit mattermost
lxc launch ubuntu:24.04 mattermost -p default -p mattermost
lxc exec mattermost -- bash

### postgres setup

https://docs.mattermost.com/deployment-guide/server/preparations.html#database-preparation

CREATE DATABASE mattermost WITH ENCODING 'UTF8' LC_COLLATE='en_US.UTF-8' LC_CTYPE='en_US.UTF-8' TEMPLATE=template0;
CREATE USER mmuser WITH PASSWORD 'mmuser-password';
GRANT ALL PRIVILEGES ON DATABASE mattermost to mmuser;

ALTER DATABASE mattermost OWNER TO mmuser;
-- Connect to the mattermost database so the schema grants below apply to the right schema
\c mattermost
ALTER SCHEMA public OWNER TO mmuser;
GRANT USAGE, CREATE ON SCHEMA public TO mmuser;

### mattermost setup

https://docs.mattermost.com/deployment-guide/server/deploy-linux.html

sudo rm /usr/share/keyrings/mattermost-archive-keyring.gpg
curl -sL -o- https://deb.packages.mattermost.com/pubkey.gpg | gpg --dearmor | sudo tee /usr/share/keyrings/mattermost-archive-keyring.gpg > /dev/null
curl -o- https://deb.packages.mattermost.com/repo-setup.sh | sudo bash -s mattermost

sudo apt update
sudo apt install mattermost -y

### mattermost config
use env vars. edit systemd service and add env file.
