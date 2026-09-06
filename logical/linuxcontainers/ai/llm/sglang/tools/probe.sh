#!/usr/bin/env bash
# Usage: probe.sh <target_tokens> [target2 ...]
# Fires filler prompts of ~N tokens at the local SGLang (port 8000 in the LXC)
# and prints what SGLang reports (actual prompt_tokens = real tokenizer count).
set -u
for t in "$@"; do
  chars=$(( t * 4 ))
  out="/tmp/probe_${t}.json"
  {
    printf '{"model": "/models/qwen3.8/gittensor-model-hub_Qwen3.8-27B-NVFP4-RTX5090", "messages": [{"role": "user", "content": "'
    yes 'lorem ipsum dolor sit amet consectetur adipiscing elit sed do eiusmod tempor' | head -c "$chars"
    printf '\\nReply with just: OK"}], "max_tokens": 5, "temperature": 0.0}'
  } > "$out"
  start=$(date +%s)
  resp=$(curl -s -m 240 https://llm.linole.org/v1/chat/completions \
    -H 'Content-Type: application/json' -d @"$out" 2>/dev/null)
  elapsed=$(( $(date +%s) - start ))
  if [ -z "$resp" ]; then
    echo "~${t}tok: CURL FAILED after ${elapsed}s (server may have restarted)"
    continue
  fi
  ptk=$(printf '%s' "$resp" | grep -oE '"prompt_tokens": *[0-9]+' | head -1 | grep -oE '[0-9]+')
  ans=$(printf '%s' "$resp" | grep -oE '"content": *"[^"]*"' | head -1 | cut -c1-80)
  err=$(printf '%s' "$resp" | grep -oE '"error"[: ].{0,160}')
  echo "~${t}tok (${chars} chars): prompt_tokens=${ptk:-?} elapsed=${elapsed}s ${ans:-} ${err:-}"
  rm -f "$out"
done
