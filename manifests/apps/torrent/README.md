# vpn in kubernetes
* https://medium.com/@s.hameedakmal/wireguard-vpn-in-a-kubernetes-cluster-e306fdc69731
* https://github.com/wg-easy/wg-easy/wiki/Using-WireGuard-Easy-with-Kubernetes
* https://nordvpn.com/blog/nordvpn-config-files/
* https://gist.github.com/bluewalk/7b3db071c488c82c604baf76a42eaad3

## wireguard in nordvpn
* nordvpn login
* nordvpn set technology nordlynx
* nordvpn connect
* ip addr -> get ip addr of nordlynx
* sudo wg show nordlynx private-key
* sudo wg show nordlynx public-key
* curl -s "https://api.nordvpn.com/v1/servers/recommendations?&filters\[servers_technologies\]\[identifier\]=wireguard_udp&limit=1"|jq -r '.[]|.hostname, .station, (.locations|.[]|.country|.city.name), (.locations|.[]|.country|.name), (.technologies|.[].metadata|.[].value), .load'

## get private_key
* docker run --rm --cap-add=NET_ADMIN -e USER=ole.klokkhammer@outlook.com -e TOKEN=xxx bubuntux/nordvpn:get_private_key

## ipv6
https://support.nordvpn.com/hc/en-us/articles/20164669224337-How-to-disable-IPv6-on-Linux

## setup
* kubectl create namespace torrent
* sudo zfs create -o quota=500M k3s/torrent-config 
* kubectl create secret generic -n torrent  torrent-secrets --from-env-file=.env
* kubectl apply -f storage.yaml
* kubectl apply -f deployment.yaml
* kubectl apply -f service.yaml