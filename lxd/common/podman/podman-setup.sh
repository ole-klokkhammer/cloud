#!/bin/bash
 
# 1. Install Podman 
sudo apt update && sudo apt install -y podman systemd-container passt

# 2. Storage Configuration
cat > /etc/containers/storage.conf << 'EOF'
[storage]
driver = "overlay"
graphroot = "/ssd/podman"
runroot = "/run/containers/storage"
EOF

# 3. Create ZFS dataset for Podman storage
#sudo zfs create -o compression=zstd -o acltype=posixacl -o xattr=sa -o atime=off -o quota=200G ssd/podman

# 4. Check the storage state
podman info --format '{{.Store.GraphRoot}}'
podman info --format '{{.Store.GraphDriverName}}'
podman info | grep -A 20 "store:"

# 5. Test Podman
podman run --rm docker.io/library/alpine:latest echo ok

# 8. check cgroup v2 is enabled
cat /sys/fs/cgroup/cgroup.controllers
# Output should include: cpu memory io
# Now you can set resource limits
podman run -d --name limited-container --memory 512m --cpus 1.0 docker.io/library/alpine:latest sleep 1h
# Verify limits are applied
podman stats --no-stream limited-container

# 9. Network Configuration (netavark)
podman info | grep networkBackend
# netavark should be listed as the network backend. If not, you may need to configure Podman to use netavark.

# 10. Enable Podman auto-update
systemctl enable --now podman-auto-update.timer
systemctl list-timers | grep podman-auto-update
