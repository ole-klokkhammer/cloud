# LXD

## setup

// init lxc
sudo lxd init --preseed < config.yaml


## web
- lxc config set core.https_address :8443

## move files

- sudo rsync -aHAX --itemize-changes --progress /ssd/lxd-configs/plex /ssd/appdata/plex