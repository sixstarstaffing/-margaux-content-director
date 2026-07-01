#!/usr/bin/env bash
# test-run.sh · one-shot Margaux proof-run on the VPS.
# Downloads the real Drive folder, extracts frames, runs her brain, prints the sheet.
# Needs: ANTHROPIC_API_KEY in the env, ffmpeg + python3 (already on Hermes), internet.
set -uo pipefail

FOLDER_URL="${MARGAUX_TEST_FOLDER:-https://drive.google.com/drive/folders/1-a3hclOTFGm03Q6ESxU9kOEQOlzJZ8r4}"

if [ -z "${ANTHROPIC_API_KEY:-}" ]; then
  echo "!! Set ANTHROPIC_API_KEY first:  export ANTHROPIC_API_KEY='sk-ant-...'"; exit 2
fi

echo "=== python venv + deps (headless, server-safe) ==="
python3 -m venv .venv && . .venv/bin/activate
pip install -q --upgrade pip
pip install -q opencv-python-headless scenedetect pillow pillow-heif gdown anthropic \
  || { echo "pip install failed"; exit 1; }

echo "=== download the real Drive folder ==="
rm -rf dl flat && mkdir -p flat
gdown --folder "$FOLDER_URL" -O dl --remaining-ok || true
# flatten every media file (handles the nested Dayinthelife subfolder + same-name dupes)
COUNT=0
while IFS= read -r -d '' f; do
  cp "$f" "flat/${RANDOM}${RANDOM}_$(basename "$f")" && COUNT=$((COUNT+1))
done < <(find dl -type f \( -iname '*.mov' -o -iname '*.mp4' -o -iname '*.heic' \
  -o -iname '*.jpg' -o -iname '*.jpeg' -o -iname '*.png' -o -iname '*.webp' \) -print0 2>/dev/null)
echo "  pulled $COUNT media files"
if [ "$COUNT" -eq 0 ]; then
  echo "!! Got 0 files. The Drive folder must be shared 'Anyone with the link' for the"
  echo "   VPS to download it (it is not logged into your Google account). Fix sharing and re-run."
  exit 1
fi

echo "=== run Margaux's brain on the real frames ==="
python deploy/sprint/test-run.py --folder flat --out routing-sheet.md
echo
echo "=== the sheet is also saved at: $(pwd)/routing-sheet.md ==="
