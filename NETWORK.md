Internet
   │
pfSense (1G in / 1G out)
   │
UniFi 8-port (1G)  ← Bottleneck for server traffic
   │
Zyxel 2.5G Switch
   │
Servers (2.5G NICs)


## ip ranges

|       Range | Typical Use                                   |
| ----------: | --------------------------------------------- |
|    .1 – .19 | Core infra (router, firewall, APs, IPMI, BMC) |
|   .20 – .39 | Physical servers                              |
|   .40 – .59 | Media devices and hubs                        |
|   .60 – .79 | Smart home devices and sensors                |
|   .80 – .99 | Cameras (IP cams, NVRs, camera bridges)       |
| .100 – .119 | Databases                                     |
| .120 – .139 | Brokers                                       |
| .140 – .179 | General apps                                  |
| .180 – .199 | Media                                         |
| .200 – .254 | DHCP pool for general devices                 |
