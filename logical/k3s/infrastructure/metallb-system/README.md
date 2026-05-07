## Installation of Metal Lb
https://metallb.universe.tf/installation/

## follow this: https://kavishgr.gitlab.io/2023/05/k3salpine/
* kubectl apply -f https://raw.githubusercontent.com/metallb/metallb/v0.15.2/config/manifests/metallb-native.yaml
* kubectl apply -f address-pool.yaml
* kubectl apply -f advertisement.yaml
 

## FRR MODE???
* kubectl apply -f peer.yaml
*  kubectl describe -n metallb-system IPAddressPool first-pool | grep Addresses -A 2
* 

# pfsense 
* https://blog.perfectra1n.com/setting-up-metallb-in-bgp-mode-with-pfsense/
* https://blog.matrixpost.net/set-up-dynamic-routing-with-frr-free-range-routing-in-pfsense-openbgpd-now-depricated/
** https://www.danmanners.com/posts/2019-02-pfsense-bgp-kubernetes/
** https://www.codepro.guru/index.php/2022/06/07/k3s-isp-deployment-metallb/)

--
AS 64512
fib-update yes
listen on 192.168.10.1
router-id 192.168.10.1
network 192.168.0.0/24

neighbor 192.168.0.2 {
    remote-as 64513
    announce all
    descr "master0"
}

neighbor 192.168.10.100 {
    remote-as 64513
    announce all
    descr "node0"
}

neighbor 192.168.10.101 {
    remote-as 64513
    announce all
    descr "node1"
}

neighbor 192.168.10.102 {
    remote-as 64513
    announce all
    descr "node2"
}
--