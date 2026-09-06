#!/usr/bin/env bash
# Deliberate OOM / overload driver for the sglang appliance, run from a client.
# Server self-heals via systemd Restart=always — the client just observes the
# crash (reset / 5xx / down) and confirms recovery.
set -u

HOST="${HOST:-0}"          # 1 = run on the appliance, hit 127.0.0.1:8000 directly (no LB 504s)
PORT="${PORT:-8000}"
LLM_BASE="${LLM_BASE:-https://llm.linole.org}"
if [ "$HOST" = "1" ]; then BASE="http://127.0.0.1:$PORT"; else BASE="$LLM_BASE"; fi
CONC="${CONC:-16}"        # client concurrency (server caps running requests at 2, surplus queues)
CTX_WORDS="${CTX_WORDS:-4000}"   # ~5.5k-token long context per request
MAXTOK="${MAXTOK:-1024}"         # long generation
WAIT="${WAIT:-90}"           # client per-request max-time (must exceed LB timeout to see true failures)
OUTD="/tmp/oom_$$"
mkdir -p "$OUTD"

ts() { date -u +%Y-%m-%dT%H:%M:%SZ; }

# hard preset only when NOT on the appliance host (LB 504s are the whole point there)
if [ "${HARD:-0}" = "1" ] && [ "$HOST" != "1" ]; then CONC=48; CTX_WORDS=8000; MAXTOK=2048; WAIT=300; fi

echo "MODE=$([ "$HOST" = 1 ] && echo appliance-direct || echo client) BASE=$BASE CONC=$CONC CTX_WORDS=$CTX_WORDS MAXTOK=$MAXTOK WAIT=$WAIT"

# ---- host-mode pre-check: GPU + memory + service state (crash forensics) ----
JLOG=""
if [ "$HOST" = "1" ]; then
  echo "=== APPUANCE PRE-STATE $(ts) ==="
  { command -v nvidia-smi >/dev/null && nvidia-smi --query-gpu=uuid,memory.used,memory.total,utilization.gpu,memory.fragmentation --format=csv; } 2>/dev/null > "$OUTD/pre_gpu.txt" || echo "no nvidia-smi"
  nvidia-smi --query-gpu=memory.used,memory.total,utilization.gpu --format=csv 2>/dev/null || true
  free -h | sed 's/^/  /'
  systemctl is-active sglang.service 2>/dev/null
  # live journal capture so we capture the real crash signature (CUDA OOM / Killed / SIGSEGV)
  JLOG="$OUTD/journal.log"
  journalctl -u sglang.service -n 0 -f --no-pager -o short-monolithic > "$JLOG" 2>&1 &
  JPID=$!
  echo "journal capture -> $JLOG (pid $JPID)"
fi

# ---- pre-state ----
echo "=== PRE $(ts) ==="
pre_health=$(curl -sS -m 15 "$BASE/health" 2>&1)
rc=$?
echo "health rc=$rc -> ${pre_health:-<empty ok>}"
echo "$pre_health" > "$OUTD/pre_health.txt"

# build a long prompt + write the full JSON payload once to a file
# (avoids ARG_MAX when the context is huge)
python3 - "$CTX_WORDS" "$MAXTOK" "$OUTD/payload.json" <<'PY'
import sys, json
n, maxtok, out = int(sys.argv[1]), int(sys.argv[2]), sys.argv[3]
text = " ".join(["lorem ipsum dolor sit amet"] * n)
json.dump({"text": text, "sampling_params": {"max_new_tokens": maxtok}}, open(out, "w"))
print("prompt_chars=", len(text))
PY
echo "payload=$OUTD/payload.json ($(wc -c < "$OUTD/payload.json") bytes)"

# ---- drive ----
echo "=== DRIVE begin $(ts) ==="
: > "$OUTD/codes.txt"
for i in $(seq 1 "$CONC"); do
  (
    # separate body, stderr, and HTTP status into files so a 504 page
    # is never mistaken for a successful generation (payload from a file, not argv)
    curl -sS --max-time "$WAIT" -o "$OUTD/body_$i" -w '%{http_code}' \
      -H 'Content-Type: application/json' \
      --data "@$OUTD/payload.json" \
      "$BASE/generate" > "$OUTD/code_$i" 2> "$OUTD/err_$i"
    rc=$?
    code=$(tr -d ' \n' < "$OUTD/code_$i" 2>/dev/null)
    [ -z "$code" ] && code="000"        # connection-level failure (reset/EOF/real-down)
    bytes=$(wc -c < "$OUTD/body_$i" 2>/dev/null || echo 0)
    echo "req=$i rc=$rc http=$code bytes=$bytes err=$(head -c 100 "$OUTD/err_$i" 2>/dev/null)" >> "$OUTD/codes.txt"
  ) &
done
wait
echo "=== DRIVE end $(ts) ==="

echo "---- request results ----"
head -n 80 "$OUTD/codes.txt"
ok=$(grep -cE 'http=2[0-9]{2}' "$OUTD/codes.txt" || true)
lb504=$(grep -cE 'http=504' "$OUTD/codes.txt" || true)
down=$(grep -cE 'http=000' "$OUTD/codes.txt" || true)   # rc!=0: reset/EOF — real OOM/kill signature
echo "summary ok=$ok lb504=$lb504 down=$down total=$CONC"
echo "---- crash signatures (http=000: connection never completed) ----"
grep -E 'http=000' "$OUTD/codes.txt" | head -n 20

# ---- recovery poll ----
echo "=== RECOVERY POLL $(ts) ==="
i=0
while [ "$i" -lt 240 ]; do
  if h=$(curl -sS -m 8 "$BASE/health" 2>/dev/null); then
    echo "health=UP after $((i*2))s ($(ts))"; break
  fi
    sleep 2; i=$((i+1))
    if [ $((i % 10)) -eq 0 ]; then echo "health=DOWN t=$((i*2))s"; fi
done

# ---- host-mode post: stop journal capture + dump crash signature ----
if [ "$HOST" = "1" ]; then
  { command -v nvidia-smi >/dev/null && nvidia-smi --query-gpu=uuid,memory.used,memory.total,utilization.gpu --format=csv; } 2>/dev/null > "$OUTD/post_gpu.txt" || true
  [ -n "$JPID" ] && kill "$JPID" 2>/dev/null
  echo "=== SERVICE $(ts) ==="
  systemctl is-active sglang.service 2>/dev/null
  echo "---- journal crash signatures (last 40 lines, filtered) ----"
  { grep -inE 'oom|killed|out of memory|cu?da.*(fail|alloc)|sigsegv|segfault|restart|exit' "$JLOG" 2>/dev/null || echo "(no OOM/crash lines found in journal window)"; } | head -n 40
  echo "---- journal tail (last 25 lines, raw) ----"
  tail -n 25 "$JLOG" 2>/dev/null || true
fi

echo "=== DONE $(ts) ==="
echo "artifacts in $OUTD"
