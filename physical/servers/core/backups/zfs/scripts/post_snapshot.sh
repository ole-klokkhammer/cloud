#!/usr/bin/env bash
###############################################################################
# post_snapshot.sh - Sanoid post-snapshot hook
#
# This script is called by sanoid after taking snapshots.
# It uploads the new snapshot(s) to S3 (streaming, no temp file).
#
# Environment variables set by sanoid:
#   SANOID_SCRIPT     = "post"
#   SANOID_TARGETS    = comma-separated dataset list
#   SANOID_SNAPNAMES  = comma-separated snapshot names (no dataset prefix)
#   SANOID_TYPES      = comma-separated types (hourly,daily,weekly,monthly,yearly)
#   SANOID_PRE_FAILURE= 0 or 1
#
# Required env (via /etc/sanoid/sanoid-s3.env):
#   S3_BUCKET, AWS_PROFILE, S3_ENDPOINT_URL
#   WEBHOOK_URL (optional)
###############################################################################
set -euo pipefail

# ------------------ Setup ------------------
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/lib.sh"

ENV_FILE="${SANOID_ENV_FILE:-/etc/sanoid/sanoid-s3.env}"
LOG_FILE="${LOG_FILE:-/var/log/sanoid/post_snapshot.log}"

load_env "$ENV_FILE"
init_s3_vars
init_log "$LOG_FILE"
setup_timeout_trap

# ------------------ Main ------------------
log "${BOLD}=== post_snapshot hook started ===${NC}"
log_info "SANOID_TARGETS=$SANOID_TARGETS"
log_info "SANOID_SNAPNAMES=$SANOID_SNAPNAMES"
log_info "SANOID_TYPES=$SANOID_TYPES"
log_info "SANOID_PRE_FAILURE=${SANOID_PRE_FAILURE:-0}"

# Abort if pre-snapshot script failed
if [[ "${SANOID_PRE_FAILURE:-0}" == "1" ]]; then
    die "pre_snapshot script failed; skipping upload"
fi

# ------------------ Upload new snapshots to S3 ------------------
IFS=',' read -ra DATASETS <<< "$SANOID_TARGETS"
IFS=',' read -ra SNAPNAMES <<< "$SANOID_SNAPNAMES"
IFS=',' read -ra TYPES <<< "${SANOID_TYPES:-}"

UPLOAD_ERRORS=0

for dataset in "${DATASETS[@]}"; do
    # Get state for this dataset - we only care about last_full for incrementals
    last_full=$(get_last_full "$dataset")
    log_info "Dataset ${BLUE}$dataset${NC}: last_full=${last_full:-<none>}"

    for i in "${!SNAPNAMES[@]}"; do
        snapname="${SNAPNAMES[$i]}"
        snap_type="${TYPES[$i]:-daily}"  # default to daily if not provided
        full_snap="${dataset}@${snapname}"
        
        # Check snapshot exists
        if ! snapshot_exists "$full_snap"; then
            log_warn "snapshot $full_snap does not exist, skipping"
            continue
        fi

        # Decide: full or incremental?
        # Incrementals are ALWAYS based on last_full (not chained)
        # This means each incremental can be restored independently: FULL + single INCR
        do_full=false
        base_snap=""

        if [[ -z "$last_full" ]]; then
            # No previous full - must do full
            do_full=true
            log_info "No previous full for $dataset, creating first full backup"
        elif should_do_full_for_type "$snap_type"; then
            # Weekly/monthly/yearly get full backups
            do_full=true
            log_info "Type '$snap_type' triggers full backup"
        else
            # Check if the FULL snapshot still exists locally (needed for zfs send -i)
            base_snap="${dataset}@${last_full}"
            if snapshot_exists "$base_snap"; then
                do_full=false
            else
                log_warn "Base snapshot $base_snap no longer exists locally, forcing full backup"
                do_full=true
            fi
        fi

        # Determine S3 key based on full or incremental
        # Full:  dataset/full/snapname.zfs.zst
        # Incr:  dataset/incr/snapname_from_base.zfs.zst
        if $do_full; then
            s3_key="${dataset}/full/${snapname}.zfs.zst"
            upload_type="full"
            log_info "Uploading ${BOLD}FULL${NC} ${BLUE}$full_snap${NC} -> ${CYAN}s3://${S3_BUCKET}/${s3_key}${NC}"
            zfs_send_cmd="zfs send $full_snap"
        else
            # Always base incremental on last_full, NOT last_uploaded
            base_name="${last_full}"
            s3_key="${dataset}/incr/${snapname}_from_${base_name}.zfs.zst"
            upload_type="incr"
            log_info "Uploading ${BOLD}INCR${NC} ${BLUE}$full_snap${NC} (from FULL: ${base_name}) -> ${CYAN}s3://${S3_BUCKET}/${s3_key}${NC}"
            zfs_send_cmd="zfs send -i ${dataset}@${base_name} $full_snap"
        fi

        # Stream: zfs send [-i base] | zstd | aws s3 cp -
        aws_err=$(mktemp)
        if $zfs_send_cmd 2>>"$LOG_FILE" \
            | zstd -3 -T0 2>>"$LOG_FILE" \
            | aws s3 cp - "s3://${S3_BUCKET}/${s3_key}" \
                --profile "$AWS_PROFILE" \
                --endpoint-url "$S3_ENDPOINT_URL" \
                2>"$aws_err"; then
            log_ok "uploaded $full_snap ($upload_type)"
            
            # Update state in S3 - only update last_full when we do a full backup
            if update_state "$dataset" "$snapname" "$upload_type"; then
                if [[ "$upload_type" == "full" ]]; then
                    log_info "State updated: last_full=$snapname"
                    last_full="$snapname"  # Update local tracking for next snapshot in this batch
                else
                    log_info "Incremental uploaded (base remains: $last_full)"
                fi
            else
                log_warn "Failed to update state in S3 (upload was successful)"
            fi
        else
            log_fail "upload of $full_snap failed: $(cat "$aws_err")"
            ((UPLOAD_ERRORS++)) || true
        fi
        rm -f "$aws_err"
    done
done

if [[ $UPLOAD_ERRORS -gt 0 ]]; then
    die "$UPLOAD_ERRORS snapshot upload(s) failed"
fi

log_ok "${GREEN}${BOLD}All snapshots uploaded successfully${NC}"

# ------------------ Webhook notification ------------------
notify "ok" "Sanoid snapshots uploaded: ${SANOID_SNAPNAMES}"

log "${BOLD}=== post_snapshot hook finished ===${NC}"
