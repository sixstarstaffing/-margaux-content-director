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
export PYTHONUNBUFFERED=1   # so the log streams live (buffering hid progress all day)

# 1) ALWAYS sync to latest code (plain 'git pull' silently stayed behind all day)
log "syncing code..."
git fetch -q origin && git reset -q --hard origin/main

# 2) config + secrets from .env.margaux (ALWAYS, so folder-id / api key / webhook
#    all load), then .key as an API-key fallback. Never pasted again.
[ -f .env.margaux ] && { set -a; . ./.env.margaux; set +a; }
if [ -z "${ANTHROPIC_API_KEY:-}" ] && [ -f .key ]; then
  export ANTHROPIC_API_KEY="$(tr -d '[:space:]' < .key)"
fi
[ -z "${ANTHROPIC_API_KEY:-}" ] && { log "FATAL: no ANTHROPIC_API_KEY (put it in .env.margaux once)"; exit 2; }

# 3) venv + deps: reuse if present, install only when missing (no reinstall every run)
[ -d .venv ] || python3 -m venv .venv
. .venv/bin/activate
python - <<'PY' 2>/dev/null || pip install -q opencv-python-headless scenedetect pillow pillow-heif gdown anthropic faster-whisper
import anthropic, cv2, scenedetect, PIL, gdown, faster_whisper  # noqa
PY

# 4) resolve the input list. If a daily Drive folder + API key are configured,
#    list it LIVE so the cron auto-picks-up each day's new content; else static arg.
IDS="${1:-deploy/sprint/test-file-ids.txt}"
if [ -n "${MARGAUX_DAILY_FOLDER_ID:-}" ] && [ -n "${GDRIVE_API_KEY:-}" ]; then
  log "listing daily Drive folder $MARGAUX_DAILY_FOLDER_ID ..."
  if python deploy/ops/list-drive-folder.py > .daily-ids.txt 2>/dev/null && [ -s .daily-ids.txt ]; then
    IDS=".daily-ids.txt"; rm -rf flat        # fresh: process exactly today's folder
    log "daily folder has $(wc -l < .daily-ids.txt) media files"
  else
    # In daily mode an empty folder = nothing dropped today. Exit clean so the cron
    # NEVER falls back to stale test footage and never sends a misleading digest.
    log "daily folder has no media today; nothing to do. exiting."
    exit 0
  fi
fi
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

# 6) deliver the 10-SECOND DIGEST to Kailin (the full sheet stays for the editor)
python deploy/ops/digest.py "$OUT" || true
log "DONE. sheet: $REPO/$OUT"
