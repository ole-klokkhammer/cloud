#!/usr/bin/env bash
# oomprobe.sh — OOM / crash-boundary test via WAN (no lxc, no nvidia-smi needed here).
set -u
BASE=${BASE:-https://llm.linole.org}
model="/models/qwen3.8/gittensor-model-hub_Qwen3.8-27B-NVFP4-RTX5090"
specs=("$@")
[ "${#specs[@]}" -eq 0 ] && specs=(165000x1 250000x1 40000x8)

mkbody(){ python3 - "$1" "$2" "$model" >"$3" <<'PY'
import json,random,sys
tok,seed=int(sys.argv[1]),int(sys.argv[2]); model=sys.argv[3]; random.seed(seed)
a="abcdef0123456789"; w=lambda: "".join(random.choice(a) for _ in range(9))
open(sys.argv[3],"w").write(json.dumps({
  "model":model,
  "messages":[{"role":"user","content":" ".join(w()+str(random.getrandbits(40)) for _ in range(tok))
              +" [Reply with just: OK]"}],
  "max_tokens":64,"temperature":0.0}))
PY
}

fire(){ # $1 label $2 body
  local r m c rc cl
  r=$(curl -s -m 900 -H 'Content-Type: application/json' -d @"$2" "$BASE/v1/chat/completions"); rc=$?
  if [ $rc -ne 0 ]; then
    if printf '%s' "$r" | grep -qiE 'out of memory'; then cl=CLASS-A-VRAM
    else cl="EOF/CLOSED (curl rc=$rc, server likely restarted)"; fi
    echo "[$1] => $cl"; return
  fi
  m=$(printf '%s' "$r"|grep -oE '"prompt_tokens":[^,]+'|head -1|tr -d '" ')
  c=$(printf '%s' "$r"|grep -oE '"completion_tokens":[^,]+'|head -1|tr -d '" ')
  cl=""
  printf '%s' "$r"|grep -qiE 'context too long|exceeds|would exceed|"code"?[: ]*"?"?400' && cl=GRACEFUL
  printf '%s' "$r"|grep -qiE 'assertionerror|can not alloc mamba|mamba cache'     && cl=CLASS-B-mamba
  printf '%s' "$r"|grep -qiE 'cuda out of memory|out of memory'                   && cl=CLASS-A-VRAM
  [ -z "$cl" ] && [ -z "$m" ] && cl="UNKNOWN (no tokens in response)"
  echo "[$1] prompt_tokens=${m:-?} completion=${c:-?} => ${cl:-OK}"
}

for spec in "${specs[@]}"; do
  tok=${spec%x*}; n=${spec##*x}; n=${n:-1}
  echo "=== ${tok}tok x ${n} (concurrent) ==="
  for c in $(seq 1 "$n"); do
    b=/tmp/oom_${tok}_${c}.json
    mkbody "$tok" "$(( $(date +%s%N | cut -c1-9) + tok + c ))" "$b"
    fire "${tok}tok/${c}" "$b" &
  done
  wait
  echo "--- (5s settle) ---"; sleep 5
done
rm -f /tmp/oom_*.json
