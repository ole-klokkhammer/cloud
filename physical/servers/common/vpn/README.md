
# setup
* create a vlan for the cloud cluster
* https://www.wundertech.net/how-to-set-up-wireguard-on-pfsense/

## wireguard
* https://www.wireguard.com/install/
* wg genkey | tee private.key | wg pubkey > public.key
* https://ubuntu.com/server/docs/using-the-vpn-as-the-default-gateway


# snap
* sudo snap connect wireguard-dtp:firewall-control
* sudo snap connect wireguard-dtp:network-control
* sudo cp linole.conf /var/snap/wireguard-dtp/current/etc
* sudo snap restart wireguard-dtp