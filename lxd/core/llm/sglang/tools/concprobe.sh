#!/usr/bin/env bash
# Usage: concprobe.sh <n_concurrent> <target_tokens>
# Fires N identical ~N-token filler prompts in PARALLEL at the endpoint and
# prints per-request latencies and completion-token counts.
set -u
N="${1:?usage: concprobe.sh <n_concurrent> <target_tokens>}"
T="${2:?usage: concprobe.sh <n_concurrent> <target_tokens>}"
CHARS=$(( T * 4 ))
OUT_DIR=$(mktemp -d)
trap 'rm -rf "$OUT_DIR"' EXIT

model="/models/qwen3.8/gittensor-model-hub_Qwen3.8-27B-NVFP4-RTX5090"

SALT="${SALT:-0}"  # set SALT=1 to append unique suffixes so KV is NOT shared
for i in $(seq 1 "$N"); do
  uuid=$(cat /proc/sys/kernel/random/uuid)
  {
    printf '{"model": "%s", "messages": [{"role": "user", "content": "' "$model"
    if [ "$SALT" = "1" ]; then
      # unique content: base64 of /dev/urandom => ~2-4 chars/token, no cache sharing
      head -c "$CHARS" /dev/urandom | base64 -w0 | head -c "$CHARS"
      printf ' [%s]' "$uuid"
    else
      yes "lorem ipsum dolor sit amet consectetur adipiscing elit sed do eiusmod tempor" | head -c "$CHARS"
    fi
    printf '\\nReply with just: OK"}], "max_tokens": 64, "temperature": 0.0}'
  } > "$OUT_DIR/req_${i}.json"

  (
    start=$(date +%s%N)
    resp=$(curl -s -m 300 https://llm.linole.org/v1/chat/completions \
      -H 'Content-Type: application/json' -d @"$OUT_DIR/req_${i}.json")
    end=$(date +%s%N)
    el=$(awk -v a="$start" -v b="$end" 'BEGIN{printf "%.1f", (b-a)/1e9}')
    ptk=$(printf '%s' "$resp" | grep -oE '"prompt_tokens": *[0-9]+' | head -1 | grep -oE '[0-9]+')
    ctk=$(printf '%s' "$resp" | grep -oE '"completion_tokens": *[0-9]+' | head -1 | grep -oE '[0-9]+')
    echo "req ${i}: prompt_tokens=${ptk:-?} completion_tokens=${ctk:-?} elapsed=${el}s"
  ) &
done
wait
echo "--- all ${N} concurrent requests done ---"
