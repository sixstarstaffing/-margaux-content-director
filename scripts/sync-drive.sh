#!/usr/bin/env bash
# sync-drive.sh · Kailin ALWAYS gives a Google Drive folder LINK. This resolves
# that link to a LOCAL working copy so the rest of the pipeline (ffmpeg /
# PySceneDetect / whisper) can actually read the video. The user never does this
# by hand: Margaux runs it as step one on any Drive link.
#
# Two ways it gets the files, in priority order:
#   1) Google Drive desktop app  · if the folder is already synced under
#      ~/Library/CloudStorage/GoogleDrive-*/, we just point at that local mirror
#      (no copy, instant). Best case.
#   2) rclone  · pull the folder by its ID to a local dir. Needs a one-time
#      `rclone config` Drive remote (see SETUP.md). Works for any link.
#
# Usage:
#   sync-drive.sh "<drive_folder_link_or_id>" [local_out_dir] [rclone_remote]
# Prints the LOCAL path to hand to triage-media.py.

set -uo pipefail

LINK="${1:?usage: sync-drive.sh <drive_folder_link_or_id> [out_dir] [remote]}"
# Production: MARGAUX_WORKDIR is set on the VPS so pulls land in the capped workdir,
# not the service user's $HOME. Falls back to $HOME/content-inbox for local dev.
OUT="${2:-${MARGAUX_WORKDIR:-$HOME/content-inbox}/$(date +%Y-%m-%d 2>/dev/null || echo drive-pull)}"
REMOTE="${3:-}"

# --- extract the folder ID from a link (or accept a bare ID) ---
ID="$LINK"
if [[ "$LINK" == *"drive.google.com"* ]]; then
  ID="$(printf '%s' "$LINK" | sed -nE 's#.*/folders/([A-Za-z0-9_-]+).*#\1#p')"
  [ -z "$ID" ] && ID="$(printf '%s' "$LINK" | sed -nE 's#.*[?&]id=([A-Za-z0-9_-]+).*#\1#p')"
fi
if [ -z "$ID" ]; then
  echo "Could not parse a Drive folder ID from: $LINK" >&2
  echo "Paste the share link (…/folders/<ID>) or the bare folder ID." >&2
  exit 1
fi

# --- 1) Google Drive desktop app mirror (instant, no copy) ---
# If a CloudStorage mount exists we cannot map ID->path directly, so this path is
# used only when the caller passes a folder NAME hint via DRIVE_FOLDER_NAME.
GDRIVE_MOUNT="$(ls -d "$HOME"/Library/CloudStorage/GoogleDrive-* 2>/dev/null | head -1 || true)"
if [ -n "${DRIVE_FOLDER_NAME:-}" ] && [ -n "$GDRIVE_MOUNT" ]; then
  HIT="$(find "$GDRIVE_MOUNT" -type d -name "$DRIVE_FOLDER_NAME" 2>/dev/null | head -1 || true)"
  if [ -n "$HIT" ]; then
    echo "$HIT"            # already local via Drive desktop, hand this path on
    exit 0
  fi
fi

# --- 2) rclone pull by folder ID ---
if command -v rclone >/dev/null 2>&1; then
  if [ -z "$REMOTE" ]; then
    REMOTE="$(rclone listremotes 2>/dev/null | sed 's/:$//' | head -1)"
  fi
  if [ -z "$REMOTE" ]; then
    echo "rclone is installed but no remote is configured. Run: rclone config" >&2
    echo "(one-time: make a Google Drive remote, see SETUP.md)" >&2
    exit 2
  fi
  mkdir -p "$OUT"
  echo "Pulling Drive folder $ID via rclone remote '$REMOTE' -> $OUT" >&2
  rclone copy "${REMOTE}:" "$OUT" \
    --drive-root-folder-id "$ID" \
    --drive-acknowledge-abuse \
    --transfers 4 --checkers 8 \
    --include "*.{jpg,jpeg,png,heic,heif,webp,mp4,mov,m4v,avi,mkv,hevc,JPG,JPEG,PNG,HEIC,HEIF,WEBP,MP4,MOV,M4V,AVI,MKV,HEVC}" \
    >&2 || { echo "rclone copy failed" >&2; exit 3; }
  echo "$OUT"
  exit 0
fi

echo "No sync path available. Install ONE of:" >&2
echo "  - Google Drive desktop app (then pass DRIVE_FOLDER_NAME=<folder name>), or" >&2
echo "  - rclone:  brew install rclone && rclone config   (SETUP.md has the steps)" >&2
exit 4
