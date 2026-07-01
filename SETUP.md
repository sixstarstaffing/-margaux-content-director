# Setup · one-time, before the first real run

The content-director processes pixels and audio locally. The Drive MCP is for the census and metadata only, it cannot hand ffmpeg a video file and a raw clip would overflow the model context. So two things must be true before Stage 1.

## 1. Drive link in, local mirror out (Margaux does this herself)
Kailin ALWAYS gives a Google Drive folder link. Margaux resolves it to a local copy with `scripts/sync-drive.sh "<link>"`, then processes the local copy. Set up ONE of the two sync paths once:
- **rclone (works everywhere, required on a headless VPS)** · `brew install rclone` then `rclone config` once to make a Google Drive remote. After that, `sync-drive.sh "<link>"` pulls the folder by its ID automatically. This is the default and the only option on Hermes/VPS.
- **Google Drive desktop app (Mac only, instant)** · if the folder is already synced under `~/Library/CloudStorage/GoogleDrive-*/`, pass `DRIVE_FOLDER_NAME="<folder name>"` and `sync-drive.sh` points at the local mirror with no copy.

The MCP is used only to LIST the folder for the coverage cross-check. Video pixels never go through the MCP. Never ask Kailin for a local path, the link is the only input.

## 2. Tooling (CPU-fine on this Mac, no GPU needed)
Two tiers. The CORE tier is what the script actually requires and it delivers real best-frame picking on its own. The OPTIONAL tier is genuinely optional, the script detects each and degrades gracefully, reporting what it skipped.

```bash
# CORE (required) · afternoon install, gives you everything that matters
brew install ffmpeg
pip install opencv-python pillow pillow-heif "scenedetect[opencv]"
```
The core gives you: HEIC normalize, PySceneDetect scene segmentation, blur/exposure reject gate, and the **OpenCV best-frame scorer** (sharpness + exposure + colorfulness). That scorer is what picks the prettiest frame per scene. You do NOT need any ML/GPU deps for it.

```bash
# OPTIONAL · transcription for talking-to-camera clips (Metal-accelerated)
brew install whisper-cpp
# then download ONE ggml model, e.g.:
#   curl -L -o ~/whisper.cpp/models/ggml-medium.bin \
#     https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-medium.bin
# point the script at it with --whisper-model PATH or env WHISPER_CPP_MODEL
```
whisper.cpp is WIRED: when speech is detected the script extracts 16k mono wav, runs whisper-cli, and returns the transcript. It runs ONLY on clips with real speech (>15% non-silent), never on b-roll. If whisper or a model is absent, talking clips are scored on visuals and the sheet says "scored on visuals only" so it is never an invisible drop.

```bash
# EXPERIMENTAL · CLIP/LAION aesthetic model. NOT required, NOT recommended yet.
# The OpenCV proxy above is the wired default. The CLIP path is detected but the
# proxy remains the scorer until validated, so DO NOT install multi-GB torch deps
# expecting a quality jump. Skip this for v1.
```

Notes:
- whisper.cpp beats faster-whisper on Mac (faster-whisper has no Metal backend).
- If `scenedetect` is missing, the script falls back to an interval sample and flags the downgrade; `scripts/sample-frames.sh` is the pure-ffmpeg last resort.

## 3. Verify
```bash
python3 ~/.claude/skills/content-director/scripts/triage-media.py --selftest
```
Prints which capabilities are live (heic / scenedetect / aesthetic / whisper) so you know what the run can and cannot do before you trust its output.

## Prior art worth reading
- `louisedesadeleer/clipify` (GitHub) · a Claude Code skill for transcript-driven clip selection and 9:16 reframe + captions. Steal its candidate-selection and reframe patterns for talking-head content. It does NOT do aesthetic scoring for silent lifestyle footage, that is this skill's add.
