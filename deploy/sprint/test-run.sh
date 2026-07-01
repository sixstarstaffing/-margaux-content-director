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

echo "=== download each file by ID (reliable for shared files; folder-download is flaky) ==="
rm -rf flat && mkdir -p flat
COUNT=0
while read -r id name; do
  [ -z "$id" ] && continue
  if gdown -q "https://drive.google.com/uc?id=$id" -O "flat/${id:0:6}_${name}" 2>/dev/null \
     && [ -s "flat/${id:0:6}_${name}" ]; then
    COUNT=$((COUNT+1))
  else
    echo "  could not fetch $name"
  fi
done < deploy/sprint/test-file-ids.txt
echo "  downloaded $COUNT media files"
if [ "$COUNT" -eq 0 ]; then
  echo "!! Got 0 files even by ID. Confirm the 'Lifestyle' folder is shared 'Anyone with the link' (that setting also applies to the files inside it)."
  exit 1
fi

echo "=== run Margaux's brain on the real frames ==="
python deploy/sprint/test-run.py --folder flat --out routing-sheet.md
echo
echo "=== the sheet is also saved at: $(pwd)/routing-sheet.md ==="
