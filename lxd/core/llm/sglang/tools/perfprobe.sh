#!/usr/bin/env bash
# perfprobe.sh — WAN probe of https://llm.linole.org (TLS, no docker/lxc).
# For the DSpark block-size/prefill A/B: run the same commands against config A
# and config B (see Makefile deploy / deploy-dspark) and compare rep 2 vs rep 3.
#
# Usage: ./tools/perfprobe.sh <target_tokens> [target2 ...]
#   examples:
#     ./tools/perfprobe.sh 8192            # cookbook reference shape
#     ./tools/perfprobe.sh 4096 8192      # typical usage + reference
#
# Each rep prints prompt/completion tokens + total elapsed, and an
# approx TPOT (total/ctk). WAN+TLS adds a roughly constant overhead per
# request, so it doesn't affect the A/B comparison — only absolute numbers.
# REPS=3 is default; rep 1 is warm-up.
set -u
[ ${#@} -eq 0 ] && {
  echo "usage: perfprobe.sh <target_tokens> [target2 ...]   (REPS=3 default)"
  exit 1
}
REPS=${REPS:-3}
URL=https://llm.linole.org/v1/chat/completions
model="/models/qwen3.8/gittensor-model-hub_Qwen3.8-27B-NVFP4-RTX5090"

for t in "$@"; do
  chars=$(( t * 4 ))
  for r in $(seq 1 "$REPS"); do
    out="/tmp/perfprobe_${t}_${r}.json"
    {
      printf '{"model": "%s", "messages": [{"role": "user", "content": "' "$model"
      yes 'lorem ipsum dolor sit amet consectetur adipiscing elit sed do eiusmod tempor' | head -c "$chars"
      printf ' [%s] Reply with just: OK"}], "max_tokens": 64, "temperature": 0.0}' "$(cat /proc/sys/kernel/random/uuid)"
    } > "$out"
    start=$(date +%s%N)
    resp=$(curl -s -m 300 "$URL" -H 'Content-Type: application/json' -d @"$out" 2>/dev/null)
    end=$(date +%s%N)
    el=$(awk -v a="$start" -v b="$end" 'BEGIN{printf "%.1f", (b-a)/1e9}')
    ptk=$(printf '%s' "$resp" | grep -oE '"prompt_tokens": *[0-9]+' | head -1 | grep -oE '[0-9]+')
    ctk=$(printf '%s' "$resp" | grep -oE '"completion_tokens": *[0-9]+' | head -1 | grep -oE '[0-9]+')
    err=$(printf '%s' "$resp" | grep -oE '"error"[: ].{0,160}')
    rm -f "$out"
    if [ -z "$resp" ] || [ -n "$err" ]; then
      echo "~${t}tok rep $r: FAILED after ${el}s ${err:-$(printf '%s' "$resp" | cut -c1-120)}"
      continue
    fi
    warm=""
    [ "$r" = 1 ] && warm=" [warm-up]"
    awk -v r="$r" -v el="$el" -v ptk="${ptk:-?}" -v ctk="${ctk:-0}" -v warm="$warm" -v t="$t" 'BEGIN{
      if (ctk+0 > 0) {
        tpot=(el/ctk)*1000
        printf "~%stok rep %s: ptk=%s ctk=%s total=%ss approx TPOT=%.0fms (≈%.0f tok/s)%s\n", t, r, ptk, ctk, el, tpot, 1000/tpot, warm
      } else {
        printf "~%stok rep %s: ptk=%s ctk=0 total=%ss (no completion tokens parsed)%s\n", t, r, ptk, el, warm
      }
    }'
  done
done
echo
echo "Compare rep 2/3 across configs A vs B. B better by >10% tok/s -> adopt B; <10% -> noise."
