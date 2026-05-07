aws s3 cp s3://zfs-core/ssd/appdata/control-plane/full/autosnap_2026-01-26_23:33:27_weekly.zfs.zst ./full-backup.zfs.zst \
  --profile zfs-core \
  --endpoint-url https://j8t7.ldn203.idrivee2-94.com

aws s3 cp s3://zfs-core/ssd/appdata/control-plane/incr/autosnap_2026-01-31_00:04:34_daily_from_autosnap_2026-01-26_23:33:27_weekly.zfs.zst ./incr-backup.zfs.zst \
  --profile zfs-core \
  --endpoint-url https://j8t7.ldn203.idrivee2-94.com


zstd -d full-backup.zfs.zst  -o full.backup.zfs
zstd -d incr-backup.zfs.zst  -o incr.backup.zfs

# On your HOST (not in the container)
sudo apt install zfsutils-linux
sudo modprobe zfs

docker run -it --privileged -v $(pwd):/backup ubuntu:22.04 bash

# Inside the container
# ------------------------------
apt update && apt install -y zfsutils-linux

# Now create the pool
truncate -s 10G /backup/zpool.img

# Create a loop device
losetup -f /backup/zpool.img
LOOP=$(losetup -j /backup/zpool.img | cut -d: -f1)
echo "Using loop device: $LOOP"

zpool create temppool $LOOP

# Restore full first (creates temppool/restored with the snapshot)
zfs recv -F temppool/restored < /backup/full.backup.zfs

# Then apply incremental (needs -F to roll back to matching snapshot)
zfs recv -F temppool/restored < /backup/incr.backup.zfs

# Copy files out
mkdir -p /backup/extracted
cp -r /temppool/restored/* /backup/extracted/

# Cleanup
zpool destroy temppool