# sanoid

## setup

### sanoid
sudo apt update
sudo apt install sanoid zstd
sudo systemctl enable --now sanoid.timer
sudo systemctl enable --now sanoid


systemctl list-timers --all | grep sanoid

### hooks
./scripts/deploy.sh

and make sure env vars are set correctly, and the aws cli is used correctly

### test
sudo zfs list -H -o name -t snapshot | grep '^ssd/appdata' | while read -r snap; do   echo "Destroying $snap";   sudo zfs destroy "$snap" || { echo "Failed: $snap"; exit 1; }; done

sudo sanoid --take-snapshots --verbose --force-update
sudo sanoid --take-snapshots --verbose