#!/usr/bin/env bash
###############################################################################
# restore.sh - Restore ZFS snapshots from S3
#
# Usage:
#   restore.sh <dataset> [snapshot]    - Restore specific or latest snapshot
#   restore.sh --list <dataset>        - List available snapshots in S3
#   restore.sh --dry-run <dataset>     - Show what would be restored
#
# Each incremental is based on a FULL backup, so restore is simple:
#   - If target is a FULL: restore just that FULL
#   - If target is an INCR: restore FULL + that single INCR
#
# Examples:
#   restore.sh ssd/appdata/myapp                    # Restore to latest
#   restore.sh ssd/appdata/myapp autosnap_2026-01-17_00:00:00_daily
#   restore.sh --list ssd/appdata/myapp
###############################################################################
set -euo pipefail

# ------------------ Setup ------------------
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/lib.sh"

ENV_FILE="${SANOID_ENV_FILE:-/etc/sanoid/sanoid-s3.env}"
LOG_FILE="${LOG_FILE:-/var/log/sanoid/restore.log}"

load_env "$ENV_FILE"
init_s3_vars
init_log "$LOG_FILE"

# ------------------ Argument Parsing ------------------
DRY_RUN=false
LIST_ONLY=false

usage() {
    echo "Usage: $0 [--list|--dry-run] <dataset> [snapshot]"
    echo ""
    echo "Options:"
    echo "  --list      List available snapshots in S3 for the dataset"
    echo "  --dry-run   Show what would be restored without doing it"
    echo ""
    echo "Examples:"
    echo "  $0 ssd/appdata/myapp                  # Restore latest snapshot"
    echo "  $0 ssd/appdata/myapp autosnap_...     # Restore specific snapshot"
    echo "  $0 --list ssd/appdata/myapp           # List available backups"
    exit 1
}

while [[ $# -gt 0 ]]; do
    case "$1" in
        --list)
            LIST_ONLY=true
            shift
            ;;
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        -h|--help)
            usage
            ;;
        *)
            break
            ;;
    esac
done

[[ $# -lt 1 ]] && usage
DATASET="$1"
TARGET_SNAP="${2:-}"

# Build common AWS args
aws_args=(--profile "$AWS_PROFILE" --endpoint-url "$S3_ENDPOINT_URL")

# ------------------ Functions ------------------

# List all snapshots in S3 for a dataset
list_snapshots() {
    local dataset="$1"
    local full_prefix="${dataset}/full/"
    local incr_prefix="${dataset}/incr/"
    
    echo "Full backups in S3:"
    aws s3 ls "s3://${S3_BUCKET}/${full_prefix}" "${aws_args[@]}" 2>/dev/null \
        | awk '{print "  " $NF}' \
        | sed 's/\.zfs\.zst$//' \
        || echo "  (none)"
    
    echo ""
    echo "Incremental backups in S3:"
    aws s3 ls "s3://${S3_BUCKET}/${incr_prefix}" "${aws_args[@]}" 2>/dev/null \
        | awk '{print "  " $NF}' \
        | sed 's/\.zfs\.zst$//' \
        || echo "  (none)"
}

# Get all full backups sorted newest first
get_full_backups() {
    local dataset="$1"
    local full_prefix="${dataset}/full/"
    
    aws s3 ls "s3://${S3_BUCKET}/${full_prefix}" "${aws_args[@]}" 2>/dev/null \
        | awk '{print $NF}' \
        | sed 's/\.zfs\.zst$//' \
        | sort -r
}

# Get all incrementals and their base snapshots
# Output format: snapname:base_snapname
get_all_incrementals() {
    local dataset="$1"
    local incr_prefix="${dataset}/incr/"
    
    aws s3 ls "s3://${S3_BUCKET}/${incr_prefix}" "${aws_args[@]}" 2>/dev/null \
        | awk '{print $NF}' \
        | sed 's/\.zfs\.zst$//' \
        | while read -r incr_file; do
            local snap_name="${incr_file%%_from_*}"
            local base_name="${incr_file#*_from_}"
            echo "${snap_name}:${base_name}"
        done
}

# Find which FULL backup an incremental is based on
find_base_for_incr() {
    local dataset="$1"
    local snap_name="$2"
    local incr_prefix="${dataset}/incr/"
    
    # Look for file: snapname_from_*.zfs.zst
    aws s3 ls "s3://${S3_BUCKET}/${incr_prefix}${snap_name}_from_" "${aws_args[@]}" 2>/dev/null \
        | awk '{print $NF}' \
        | sed 's/\.zfs\.zst$//' \
        | head -1 \
        | sed "s/^${snap_name}_from_//"
}

# Check if snapshot exists as a full backup
is_full_backup() {
    local dataset="$1"
    local snap_name="$2"
    local full_key="${dataset}/full/${snap_name}.zfs.zst"
    
    aws s3 ls "s3://${S3_BUCKET}/${full_key}" "${aws_args[@]}" &>/dev/null
}

# Get the latest snapshot (full or incremental)
get_latest_snapshot() {
    local dataset="$1"
    
    # Combine fulls and incrementals, sort by timestamp, take latest
    {
        get_full_backups "$dataset"
        get_all_incrementals "$dataset" | cut -d: -f1
    } | sort -r | head -1
}

# Restore a snapshot stream from S3
restore_stream() {
    local s3_key="$1"
    local description="$2"
    
    if $DRY_RUN; then
        log_info "[DRY-RUN] Would restore: $description"
        log_info "[DRY-RUN] aws s3 cp s3://${S3_BUCKET}/${s3_key} - | zstd -d | zfs recv ..."
        return 0
    fi
    
    log_info "Restoring: $description"
    log_info "Source: s3://${S3_BUCKET}/${s3_key}"
    
    aws s3 cp "s3://${S3_BUCKET}/${s3_key}" - "${aws_args[@]}" \
        | zstd -d \
        | zfs recv -F "${DATASET}"
}

# ------------------ Main ------------------

log "${BOLD}=== restore.sh started ===${NC}"
log_info "Dataset: $DATASET"
log_info "Target snapshot: ${TARGET_SNAP:-<latest>}"

if $LIST_ONLY; then
    list_snapshots "$DATASET"
    exit 0
fi

# Determine target snapshot
if [[ -z "$TARGET_SNAP" ]]; then
    TARGET_SNAP=$(get_latest_snapshot "$DATASET")
    if [[ -z "$TARGET_SNAP" ]]; then
        die "No backups found in S3 for $DATASET"
    fi
    log_info "Latest snapshot: $TARGET_SNAP"
fi

# Determine if target is a FULL or INCR
if is_full_backup "$DATASET" "$TARGET_SNAP"; then
    # Target is a full backup - just restore it
    FULL_SNAP="$TARGET_SNAP"
    INCR_SNAP=""
    log_info "Target is a FULL backup"
else
    # Target is an incremental - find its base FULL
    BASE_SNAP=$(find_base_for_incr "$DATASET" "$TARGET_SNAP")
    if [[ -z "$BASE_SNAP" ]]; then
        die "Cannot find incremental backup for $TARGET_SNAP in S3"
    fi
    
    FULL_SNAP="$BASE_SNAP"
    INCR_SNAP="$TARGET_SNAP"
    log_info "Target is an INCR backup based on FULL: $FULL_SNAP"
fi

# Summary
echo ""
log_info "${BOLD}Restore plan:${NC}"
log_info "  1. Full: $FULL_SNAP"
if [[ -n "$INCR_SNAP" ]]; then
    log_info "  2. Incr: $INCR_SNAP"
fi
echo ""

if $DRY_RUN; then
    log_warn "DRY RUN - no changes will be made"
fi

# Confirm
if ! $DRY_RUN; then
    read -p "Proceed with restore? This will overwrite ${DATASET}. [y/N] " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        log_warn "Restore cancelled"
        exit 1
    fi
fi

# Restore full backup
full_key="${DATASET}/full/${FULL_SNAP}.zfs.zst"
restore_stream "$full_key" "Full backup: $FULL_SNAP"

# Restore incremental if needed
if [[ -n "$INCR_SNAP" ]]; then
    incr_key="${DATASET}/incr/${INCR_SNAP}_from_${FULL_SNAP}.zfs.zst"
    restore_stream "$incr_key" "Incremental: $INCR_SNAP"
fi

log_ok "${GREEN}${BOLD}Restore completed successfully${NC}"
log "${BOLD}=== restore.sh finished ===${NC}"
