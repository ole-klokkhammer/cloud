#!/usr/bin/env bash
###############################################################################
# pruning_script.sh - Sanoid pruning hook
#
# This script is called by sanoid AFTER a snapshot is successfully deleted.
# It deletes the corresponding S3 object.
#
# Environment variables set by sanoid:
#   SANOID_SCRIPT   = "prune"
#   SANOID_TARGET   = dataset name (e.g., ssd/appdata/myapp)
#   SANOID_SNAPNAME = snapshot name (e.g., autosnap_2026-01-17_12:00:00_hourly)
#
# Required env (via /etc/sanoid/sanoid-s3.env):
#   S3_BUCKET, AWS_PROFILE, S3_ENDPOINT_URL
###############################################################################
set -euo pipefail

# ------------------ Setup ------------------
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/lib.sh"

ENV_FILE="${SANOID_ENV_FILE:-/etc/sanoid/sanoid-s3.env}"
LOG_FILE="${LOG_FILE:-/var/log/sanoid/pruning_script.log}"

load_env "$ENV_FILE"
init_s3_vars
init_log "$LOG_FILE"
setup_timeout_trap

# ------------------ Main ------------------
log "${BOLD}=== pruning_script hook started ===${NC}"
log_info "SANOID_TARGET=$SANOID_TARGET"
log_info "SANOID_SNAPNAME=$SANOID_SNAPNAME"

# Build common AWS args
aws_args=(--profile "$AWS_PROFILE" --endpoint-url "$S3_ENDPOINT_URL")

# With the new incremental strategy (all incrs based on FULL, not chained),
# snapshots can be in:
#   dataset/full/snapname.zfs.zst         (full backup)
#   dataset/incr/snapname_from_*.zfs.zst  (incremental backup)
#   dataset/snapname.zfs.zst              (legacy flat path)
#
# If this is a FULL snapshot being pruned, we must also delete all incrementals
# based on it (they become useless without their FULL base)

deleted=false
aws_err=$(mktemp)

# Try full path
full_key="${SANOID_TARGET}/full/${SANOID_SNAPNAME}.zfs.zst"
log_info "Trying ${CYAN}s3://${S3_BUCKET}/${full_key}${NC}"
if aws s3 rm "s3://${S3_BUCKET}/${full_key}" "${aws_args[@]}" 2>"$aws_err"; then
    log_ok "deleted $full_key"
    deleted=true
    
    # This was a FULL backup - delete all incrementals based on it
    base_pattern="${SANOID_TARGET}/incr/"
    log_info "Deleting all incrementals based on pruned FULL: ${SANOID_SNAPNAME}"
    orphaned=$(aws s3 ls "s3://${S3_BUCKET}/${base_pattern}" "${aws_args[@]}" 2>/dev/null \
        | awk '{print $NF}' \
        | grep "_from_${SANOID_SNAPNAME}\.zfs\.zst$" || true)
    for orphan_file in $orphaned; do
        orphan_key="${base_pattern}${orphan_file}"
        log_warn "Deleting orphaned incremental: $orphan_key"
        aws s3 rm "s3://${S3_BUCKET}/${orphan_key}" "${aws_args[@]}" 2>/dev/null || true
    done
fi

# Try incremental path (this snapshot might be an incremental)
if ! $deleted; then
    incr_prefix="${SANOID_TARGET}/incr/${SANOID_SNAPNAME}_from_"
    log_info "Looking for incremental matching ${CYAN}${incr_prefix}*${NC}"
    incr_files=$(aws s3 ls "s3://${S3_BUCKET}/${incr_prefix}" "${aws_args[@]}" 2>/dev/null | awk '{print $NF}' || true)
    for incr_file in $incr_files; do
        incr_key="${SANOID_TARGET}/incr/${incr_file}"
        if aws s3 rm "s3://${S3_BUCKET}/${incr_key}" "${aws_args[@]}" 2>"$aws_err"; then
            log_ok "deleted $incr_key"
            deleted=true
        fi
    done
fi

# Try legacy flat path (for backwards compatibility)
if ! $deleted; then
    legacy_key="${SANOID_TARGET}/${SANOID_SNAPNAME}.zfs.zst"
    log_info "Trying legacy path ${CYAN}s3://${S3_BUCKET}/${legacy_key}${NC}"
    if aws s3 rm "s3://${S3_BUCKET}/${legacy_key}" "${aws_args[@]}" 2>"$aws_err"; then
        log_ok "deleted $legacy_key (legacy)"
        deleted=true
    fi
fi

if ! $deleted; then
    log_warn "No S3 object found for ${SANOID_SNAPNAME} (may predate S3 backup)"
fi

rm -f "$aws_err"

log "${BOLD}=== pruning_script hook finished ===${NC}"
