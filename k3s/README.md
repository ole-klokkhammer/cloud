#


## pfsense 

server:
    local-zone: "cluster.local." static
    forward-zone:
        name: "cluster.local."
        forward-addr: 192.168.10.211