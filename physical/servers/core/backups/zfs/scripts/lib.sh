#!/usr/bin/env bash
###############################################################################
# lib.sh - Shared utilities for sanoid hook scripts
#
# Source this file at the top of your scripts:
#   SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
#   source "${SCRIPT_DIR}/lib.sh"
###############################################################################

# ------------------ Colors ------------------
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# ------------------ Logging ------------------
# LOG_FILE must be set before sourcing this file
# No timestamps - systemd/journald adds them automatically
log()      { echo -e "$*" | tee -a "${LOG_FILE:-/dev/null}"; }
log_info() { echo -e "${CYAN}INFO${NC}: $*" | tee -a "${LOG_FILE:-/dev/null}"; }
log_ok()   { echo -e "${GREEN}OK${NC}: $*" | tee -a "${LOG_FILE:-/dev/null}"; }
log_warn() { echo -e "${YELLOW}WARN${NC}: $*" | tee -a "${LOG_FILE:-/dev/null}"; }
log_fail() { echo -e "${RED}FAIL${NC}: $*" | tee -a "${LOG_FILE:-/dev/null}"; }
log_err()  { echo -e "${RED}${BOLD}ERROR${NC}: $*" | tee -a "${LOG_FILE:-/dev/null}"; }

# ------------------ Notifications ------------------
# WEBHOOK_URL must be set (can be empty) before using notify
notify() {
    local status="$1" msg="$2"
    if [[ -n "${WEBHOOK_URL:-}" ]]; then
        curl -fsS -m 10 "$WEBHOOK_URL" \
            -H "Content-Type: application/json" \
            -d "{\"status\": \"$status\", \"message\": \"$msg\"}" || true
    fi
}

# ------------------ Error Handling ------------------
die() { 
    log_err "$*"
    notify "error" "$*"
    exit 1
}

# ------------------ Configuration ------------------
# Load environment from file (call after setting ENV_FILE)
load_env() {
    local env_file="${1:-/etc/sanoid/sanoid-s3.env}"
    if [[ -f "$env_file" ]]; then
        # shellcheck source=/dev/null
        source "$env_file"
    fi
}

# Set safe defaults for S3 variables
init_s3_vars() {
    S3_BUCKET="${S3_BUCKET:-}"
    AWS_PROFILE="${AWS_PROFILE:-}"
    S3_ENDPOINT_URL="${S3_ENDPOINT_URL:-}"
    WEBHOOK_URL="${WEBHOOK_URL:-}"
}

# Ensure log directory exists
init_log() {
    local log_file="${1:-$LOG_FILE}"
    mkdir -p "$(dirname "$log_file")"
}

# ------------------ Traps ------------------
# Setup timeout trap for SIGALRM (call after notify is available)
setup_timeout_trap() {
    trap 'log_err "TIMEOUT: script killed by SIGALRM"; notify "error" "Script timed out (SIGALRM)"; exit 142' ALRM
}

# ------------------ State Management ------------------
# State is stored in S3 as JSON: s3://bucket/prefix/dataset/_state.json
# Format: {"last_full": "snapname", "last_uploaded": "snapname"}
#
# Requires: S3_BUCKET, S3_PREFIX, AWS_PROFILE, S3_ENDPOINT_URL to be set

# Build common aws CLI args
_aws_s3_args() {
    local args=()
    [[ -n "${AWS_PROFILE:-}" ]] && args+=(--profile "$AWS_PROFILE")
    [[ -n "${S3_ENDPOINT_URL:-}" ]] && args+=(--endpoint-url "$S3_ENDPOINT_URL")
    echo "${args[*]}"
}

# Get the state file for a dataset
# Usage: get_state_file "pool/dataset"
# Returns JSON or empty string if not found
get_state_file() {
    local dataset="$1"
    local s3_key="${dataset}/_state.json"
    local aws_args
    read -ra aws_args <<< "$(_aws_s3_args)"

    aws s3 cp "s3://${S3_BUCKET}/${s3_key}" - "${aws_args[@]}" 2>/dev/null || echo ""
}

# Set the state file for a dataset
# Usage: set_state_file "pool/dataset" '{"last_full": "snap1", "last_uploaded": "snap2"}'
set_state_file() {
    local dataset="$1"
    local state_json="$2"
    local s3_key="${dataset}/_state.json"
    local aws_args
    read -ra aws_args <<< "$(_aws_s3_args)"

    echo "$state_json" | aws s3 cp - "s3://${S3_BUCKET}/${s3_key}" "${aws_args[@]}" 2>/dev/null
}

# Get last uploaded snapshot name for a dataset
# Usage: get_last_uploaded "pool/dataset"
# Returns: snapshot name (without dataset prefix) or empty string
get_last_uploaded() {
    local dataset="$1"
    local state
    state=$(get_state_file "$dataset")
    [[ -z "$state" ]] && echo "" && return

    # Parse JSON with jq if available, otherwise grep
    if command -v jq &>/dev/null; then
        echo "$state" | jq -r '.last_uploaded // ""'
    else
        echo "$state" | grep -oP '"last_uploaded"\s*:\s*"\K[^"]+' || echo ""
    fi
}

# Get last full snapshot name for a dataset
# Usage: get_last_full "pool/dataset"
# Returns: snapshot name (without dataset prefix) or empty string
get_last_full() {
    local dataset="$1"
    local state
    state=$(get_state_file "$dataset")
    [[ -z "$state" ]] && echo "" && return

    if command -v jq &>/dev/null; then
        echo "$state" | jq -r '.last_full // ""'
    else
        echo "$state" | grep -oP '"last_full"\s*:\s*"\K[^"]+' || echo ""
    fi
}

# Update state after successful upload
# Usage: update_state "pool/dataset" "snapname" "full|incr"
update_state() {
    local dataset="$1"
    local snapname="$2"
    local upload_type="$3"  # "full" or "incr"

    local last_full last_uploaded state_json

    if [[ "$upload_type" == "full" ]]; then
        last_full="$snapname"
        last_uploaded="$snapname"
    else
        # For incremental, keep the last_full, update last_uploaded
        last_full=$(get_last_full "$dataset")
        last_uploaded="$snapname"
    fi

    state_json="{\"last_full\": \"${last_full}\", \"last_uploaded\": \"${last_uploaded}\"}"
    set_state_file "$dataset" "$state_json"
}

# Check if a local snapshot exists
# Usage: snapshot_exists "pool/dataset@snapname"
snapshot_exists() {
    local full_snap="$1"
    zfs list -t snapshot -H -o name "$full_snap" &>/dev/null
}

# Determine if we should do a full backup based on snapshot type
# Usage: should_do_full "daily" 
# Returns: 0 (true) for full, 1 (false) for incremental
# Override with FULL_SNAPSHOT_TYPES env var (comma-separated list)
should_do_full_for_type() {
    local snap_type="$1"
    # Default: full for weekly, monthly, yearly
    local full_types="${FULL_SNAPSHOT_TYPES:-weekly,monthly,yearly}"

    [[ ",$full_types," == *",$snap_type,"* ]]
}
