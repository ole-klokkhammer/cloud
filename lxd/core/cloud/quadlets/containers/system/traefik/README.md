# traefik

## setup
sudo zfs create -o compression=lz4 -o atime=off -o xattr=sa -o acltype=posixacl -o recordsize=1M ssd/appdata/traefik

## pfsense wildcard domains
services - dns-resolver - custom options:

local-zone: "core-cloud.homelan" static
local-data: "core-cloud.homelan A 192.168.10.152"