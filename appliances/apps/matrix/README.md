# matrix synapse
- https://element-hq.github.io/synapse/latest/setup/installation.html
- https://matrix.org/ecosystem/clients/
- 


## setup

## Disk
sudo zfs create -o compression=lz4 -o atime=off -o xattr=sa -o acltype=posixacl -o recordsize=1M ssd/appdata/matrix

### lxc
- lxc profile create matrix
- lxc profile edit matrix
- lxc launch ubuntu:24.04 matrix -p default -p matrix
- lxc exec matrix -- bash 


### dependencies
sudo apt update
sudo apt install -y lsb-release wget apt-transport-https
sudo wget -O /usr/share/keyrings/matrix-org-archive-keyring.gpg https://packages.matrix.org/debian/matrix-org-archive-keyring.gpg
echo "deb [signed-by=/usr/share/keyrings/matrix-org-archive-keyring.gpg] https://packages.matrix.org/debian/ $(lsb_release -cs) main" |
    sudo tee /etc/apt/sources.list.d/matrix-org.list
sudo apt update
sudo apt install matrix-synapse-py3
 

### Setup database
sudo apt install -y postgresql postgresql-contrib

// synapse need C collation
CREATE DATABASE matrix WITH ENCODING='UTF8' LC_COLLATE='C' LC_CTYPE='C' TEMPLATE template0;
CREATE USER matrix WITH PASSWORD 'xxxx';
GRANT ALL ON DATABASE matrix TO matrix;
GRANT ALL PRIVILEGES  ON SCHEMA public TO matrix;
ALTER SCHEMA public OWNER TO matrix;

### config
sudo nano /etc/matrix-synapse/homeserver.yaml
-> insert the config
-> gnerate keys for each secret:
for secret in macaroon.secret registration.shared.secret form.secret; do 
  openssl rand -hex 32 | sudo tee /etc/matrix-synapse/homeserver.$secret > /dev/null
done

// then
sudo systemctl restart matrix-synapse


### Registering users
- https://element-hq.github.io/synapse/latest/setup/installation.html?highlight=register_new_matrix_user#registering-a-user

register_new_matrix_user -c homeserver.yaml


### Keycloak?
https://element-hq.github.io/synapse/latest/openid.html?highlight=keycloa#keycloak