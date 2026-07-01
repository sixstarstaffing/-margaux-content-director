#!/usr/bin/env bash
# sample-frames.sh · ffmpeg-only FALLBACK frame sampler.
# Prefer scripts/triage-media.py (PySceneDetect + blur gate + aesthetic pick).
# Use this only when the Python libs are unavailable.
#
# Operates on a LOCAL video path (sync the Drive folder down first, see SETUP.md).
# One bad clip does NOT abort a batch: per-clip work is wrapped, not under `set -e`.
#
# Usage: sample-frames.sh <local_video> [out_dir] [interval_s] [scene_threshold]
# Defaults: out = ./frames-<base>, interval = 1s (tight, catches the good 2s), scene = 0.30

set -uo pipefail   # NOT -e: a single corrupt clip must not kill a batch run

VIDEO="${1:?usage: sample-frames.sh <local_video> [out_dir] [interval_s] [scene_threshold]}"
BASE="$(basename "${VIDEO%.*}")"
OUT="${2:-./frames-${BASE}}"
INTERVAL="${3:-1}"
SCENE="${4:-0.30}"
MAX_FRAMES=40   # hard cap so a shaky clip cannot dump hundreds of JPGs

if ! command -v ffmpeg >/dev/null 2>&1; then
  echo "ffmpeg not found. brew install ffmpeg" >&2; exit 1
fi
if [ ! -f "$VIDEO" ]; then
  echo "Not a local file: $VIDEO. Sync the Drive folder down first (SETUP.md)." >&2; exit 1
fi
mkdir -p "$OUT"

# interval frames (1s so the good 2 seconds are never skipped)
ffmpeg -hide_banner -loglevel error -i "$VIDEO" \
  -vf "fps=1/${INTERVAL}" -frames:v "$MAX_FRAMES" -q:v 3 \
  "${OUT}/interval_%03d.jpg" || echo "interval pass failed for $VIDEO" >&2

# scene-change frames
ffmpeg -hide_banner -loglevel error -i "$VIDEO" \
  -vf "select='gt(scene,${SCENE})'" -vsync vfr -frames:v "$MAX_FRAMES" -q:v 3 \
  "${OUT}/scene_%03d.jpg" 2>/dev/null || true

COUNT="$(find "$OUT" -maxdepth 1 -name '*.jpg' | wc -l | tr -d ' ')"
echo "Sampled ${COUNT} frames to: ${OUT} (fallback mode, weaker than triage-media.py)"
echo "NOTE: no blur/exposure gate and no aesthetic pick in fallback. Prefer triage-media.py."
