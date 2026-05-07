# fans

ipmitool -H 192.168.10.226 -U ADMIN -P ADMIN raw 0x30 0x70 0x66 0x01 0x00 0x1E
ipmitool -H 192.168.10.226 -U ADMIN -P ADMIN raw 0x30 0x70 0x66 0x01 0x01 0x1E

## cron
@reboot sleep 60 && ipmitool -H 192.168.10.226 -U ADMIN -P ADMIN raw 0x30 0x70 0x66 0x01 0x00 0x1E; ipmitool -H 192.168.10.226 -U ADMIN -P ADMIN raw 0x30 0x70 0x66 0x01 0x01 0x1E;
@reboot sleep 60 && /usr/bin/ipmitool -H 192.168.10.226 -U ADMIN -P ADMIN sensor thresh FANA lower 0 0 0; /usr/bin/ipmitool -H 192.168.10.226 -U ADMIN -P ADMIN sensor thresh FANB lower 0 0 0; /usr/bin/ipmitool -H 192.168.10.226 -U ADMIN -P ADMIN raw 0x30 0x45 0x01 0x01; /usr/bin/ipmitool -H 192.168.10.226 -U ADMIN -P ADMIN raw 0x30 0x70 0x66 0x01 0x00 0x1E; /usr/bin/ipmitool -H 192.168.10.226 -U ADMIN -P ADMIN raw 0x30 0x70 0x66 0x01 0x01 0x1E