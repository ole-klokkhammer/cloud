#!/bin/bash
# Fix Supermicro fan thresholds and mode for Noctua (low-RPM) fans.
# Usage: ./fix-fans.sh [BMC_IP] [USER] [PASS]
#
# This script:
#   1. Sets FANA/FANB lower critical threshold to 0 RPM (prevents false alerts)
#   2. Sets fan mode to Optimal (quietest automatic mode)
#   3. Clears the IPMI event log
#
# Can also be run at boot via cron (@reboot) or a systemd service.

set -euo pipefail

BMC_IP="${1:-192.168.10.226}"
BMC_USER="${2:-ADMIN}"
BMC_PASS="${3:-ADMIN}"

IPMI="ipmitool -H $BMC_IP -U $BMC_USER -P $BMC_PASS"

echo "==> Targeting BMC at $BMC_IP"

# Lower critical thresholds for FANA and FANB to 0 RPM
# (the 'lower 0 0 0' sets lnr/lcr/lnc — only lcr is supported, others error harmlessly)
echo "==> Setting FANA lower critical threshold to 0 RPM..."
$IPMI sensor thresh FANA lower 0 0 0 2>/dev/null || true

echo "==> Setting FANB lower critical threshold to 0 RPM..."
$IPMI sensor thresh FANB lower 0 0 0 2>/dev/null || true

# Set fan mode to Optimal (0x02)
# Modes: 0x00=Standard, 0x01=Full, 0x02=Optimal, 0x04=Heavy IO
echo "==> Setting fan mode to Optimal..."
$IPMI raw 0x30 0x45 0x01 0x02

# Clear event log (optional — removes old fan alert spam)
echo "==> Clearing IPMI event log..."
$IPMI sel clear

# Verify
sleep 3
echo ""
echo "==> Current fan readings:"
$IPMI sensor list | grep -i fan
echo ""
echo "==> FANA/FANB thresholds:"
$IPMI sdr get "FANA" "FANB" | grep -E "Sensor ID|Lower critical"
echo ""
echo "Done. Fans should quiet down within ~30 seconds."
