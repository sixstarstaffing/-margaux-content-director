#!/usr/bin/env bash
# margaux-run.sh · the ONE robust way to run Margaux. Cron-safe and disconnect-safe.
# Fixes every failure from the manual era: stale git, dropped SSH, missing key,
# stale output, repeated 2.4GB re-downloads.
#
# Run by hand (survives disconnects):
#   cd /root/margaux-test && nohup bash deploy/ops/margaux-run.sh [id_list] >/dev/null 2>&1 &
# Or let cron run it daily (see OPERATIONS.md). Read the newest sheet in ./sheets/.
set -uo pipefail
REPO="${MARGAUX_REPO:-/root/margaux-test}"
cd "$REPO" 2>/dev/null || { echo "FATAL: repo not at $REPO (set MARGAUX_REPO)"; exit 1; }
log(){ echo "[$(date '+%F %T')] $*"; }

# 1) ALWAYS sync to latest code (plain 'git pull' silently stayed behind all day)
log "syncing code..."
git fetch -q origin && git reset -q --hard origin/main

# 2) key from a STORED file, never pasted again. Prefers .env.margaux, then .key.
if [ -z "${ANTHROPIC_API_KEY:-}" ]; then
  [ -f .env.margaux ] && { set -a; . ./.env.margaux; set +a; }
  [ -z "${ANTHROPIC_API_KEY:-}" ] && [ -f .key ] && \
    export ANTHROPIC_API_KEY="$(tr -d '[:space:]' < .key)"
fi
[ -z "${ANTHROPIC_API_KEY:-}" ] && { log "FATAL: no ANTHROPIC_API_KEY (put it in .env.margaux once)"; exit 2; }

# 3) venv + deps: reuse if present, install only when missing (no reinstall every run)
[ -d .venv ] || python3 -m venv .venv
. .venv/bin/activate
python - <<'PY' 2>/dev/null || pip install -q opencv-python-headless scenedetect pillow pillow-heif gdown anthropic
import anthropic, cv2, scenedetect, PIL, gdown  # noqa
PY

# 4) download by id list; SKIP files already present (no more 2.4GB every time)
IDS="${1:-deploy/sprint/test-file-ids.txt}"
mkdir -p flat
log "downloading from $IDS (skipping ones already here)..."
n=0
while read -r id name; do
  [ -z "$id" ] && continue
  f="flat/${id:0:6}_${name}"
  if [ -s "$f" ]; then n=$((n+1)); continue; fi
  gdown -q "https://drive.google.com/uc?id=$id" -O "$f" 2>/dev/null && [ -s "$f" ] && n=$((n+1))
done < "$IDS"
log "have $n media files"
[ "$n" -eq 0 ] && { log "FATAL: 0 files (is the Drive folder shared 'Anyone with the link'?)"; exit 3; }

# 5) run, TIMESTAMPED output so nothing is ever stale/confused
mkdir -p sheets
OUT="sheets/routing-sheet-$(date +%F-%H%M).md"
log "running Margaux -> $OUT"
python deploy/sprint/test-run.py --folder flat --out "$OUT"

# 6) optional: deliver a heads-up to Discord so you never open the terminal
if [ -n "${DISCORD_BUILD_WEBHOOK:-}" ]; then
  HEAD="$(sed -n '1,12p' "$OUT")"
  python - "$DISCORD_BUILD_WEBHOOK" "$OUT" "$HEAD" <<'PY' 2>/dev/null || true
import json,sys,urllib.request
wh,out,head=sys.argv[1],sys.argv[2],sys.argv[3]
msg=f"**Margaux sheet ready** ({out})\n```\n{head[:1600]}\n```"
urllib.request.urlopen(urllib.request.Request(wh,data=json.dumps({"content":msg}).encode(),headers={"Content-Type":"application/json"}),timeout=15)
PY
fi
log "DONE. sheet: $REPO/$OUT"
