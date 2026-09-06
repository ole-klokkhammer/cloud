# traefik

## setup
we need the socket for this
systemctl enable --now podman.socket

## make deploy

## pfsense wildcard domains
services - dns-resolver - custom options:

local-zone: "core-cloud.homelan" static
local-data: "core-cloud.homelan A 192.168.10.152"