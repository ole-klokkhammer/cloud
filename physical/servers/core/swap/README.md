# Swap settings

keep 16gb swap for safety

## commands
sudo sysctl -w vm.swappiness=1
sudo sysctl -w vm.vfs_cache_pressure=50

ssd/lxd/containers/redis