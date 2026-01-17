#!/usr/bin/env bash
###############################################################################
# install-sanoid-hooks.sh
# Installs the sanoid hook scripts (post_snapshot + pruning) and env file
###############################################################################
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "Installing sanoid S3 hook scripts..."

# Create directories
sudo mkdir -p /usr/local/sanoid/scripts
sudo mkdir -p /var/log/sanoid
sudo mkdir -p /etc/sanoid

# Copy scripts
sudo cp "$SCRIPT_DIR/lib.sh" /usr/local/sanoid/scripts/lib.sh
sudo cp "$SCRIPT_DIR/post_snapshot.sh" /usr/local/sanoid/scripts/post_snapshot.sh
sudo cp "$SCRIPT_DIR/pruning_script.sh" /usr/local/sanoid/scripts/pruning_script.sh
sudo cp "$SCRIPT_DIR/restore.sh" /usr/local/sanoid/scripts/restore.sh
sudo chmod +x /usr/local/sanoid/scripts/lib.sh
sudo chmod +x /usr/local/sanoid/scripts/post_snapshot.sh
sudo chmod +x /usr/local/sanoid/scripts/pruning_script.sh
sudo chmod +x /usr/local/sanoid/scripts/restore.sh

# Copy env example if env file doesn't exist
if [[ ! -f /etc/sanoid/sanoid-s3.env ]]; then
    sudo cp "$SCRIPT_DIR/post_snapshot.env.example" /etc/sanoid/sanoid-s3.env
    echo "Created /etc/sanoid/sanoid-s3.env - please edit with your settings"
else
    echo "/etc/sanoid/sanoid-s3.env already exists, not overwriting"
fi

# Ensure log directory is writable
sudo chown root:root /var/log/sanoid
sudo chmod 755 /var/log/sanoid

echo ""
echo "Installation complete!"
echo ""
echo "Next steps:"
echo "  1. Edit /etc/sanoid/sanoid-s3.env with your S3 settings"
echo "  2. Ensure sanoid.conf has:"
echo "       autoprune = yes"
echo "       post_snapshot_script = /usr/local/sanoid/scripts/post_snapshot.sh"
echo "       pruning_script = /usr/local/sanoid/scripts/pruning_script.sh"
echo "  3. Test with: sudo sanoid --take-snapshots --verbose"
echo "  4. Check logs: tail -f /var/log/sanoid/sanoid-s3.log"
echo ""
echo "Required packages: awscli, zstd"
echo "  sudo apt install awscli zstd"
