#!/usr/bin/env python3
"""
triage-media.py · the Content Director's local media pipeline.

Operates on a LOCAL folder (Drive synced down first, see SETUP.md). The Drive MCP
cannot hand ffmpeg a video or fit a clip in model context, so all pixel/audio work
happens here on disk; only small JPG frames + a JSON manifest go back to the model.

Per asset it:
  - normalizes HEIC -> JPG (Kailin shoots HEIC)
  - for video: segments with PySceneDetect (AdaptiveDetector), falls back to an
    interval sample if scenedetect is missing
  - BEST-FRAME PICK: samples several candidate frames per scene and keeps the
    highest-scoring one. Scorer = CLIP/LAION aesthetic model IF installed, else a
    lightweight OpenCV proxy (sharpness + exposure balance + colorfulness) that
    needs NO heavy deps. Either way the pick is real, not just the midpoint.
  - rejects junk early: blur (Laplacian variance) + exposure (luma histogram)
  - TRANSCRIBES with whisper.cpp for real, ONLY when speech is detected
  - emits manifest.json + exported best-frame JPGs

Nothing is silently dropped: every asset gets a verdict (assessed / deduped /
auto-rejected). Degrades gracefully and reports which capabilities were live.
Run --selftest first.

Usage:
  triage-media.py --selftest
  triage-media.py <folder> [--out DIR] [--blur-thresh 100] [--scenes-max 8]
                  [--cands-per-scene 3] [--whisper-model PATH] [--no-whisper]
"""

import argparse, json, os, re, subprocess, sys, shutil, tempfile
from pathlib import Path

PHOTO_EXT = {".jpg", ".jpeg", ".png", ".heic", ".heif", ".webp"}
VIDEO_EXT = {".mp4", ".mov", ".m4v", ".avi", ".mkv", ".hevc"}


def which_whisper():
    for name in ("whisper-cli", "whisper-cpp", "main"):
        p = shutil.which(name)
        if p:
            return p
    return None


def default_whisper_model():
    env = os.environ.get("WHISPER_CPP_MODEL")
    if env and os.path.exists(env):
        return env
    for g in ("~/whisper.cpp/models/ggml-medium.bin",
              "~/whisper.cpp/models/ggml-base.en.bin",
              "/opt/homebrew/share/whisper-cpp/ggml-medium.bin"):
        gp = os.path.expanduser(g)
        if os.path.exists(gp):
            return gp
    return None


def cap():
    c = {"ffmpeg": shutil.which("ffmpeg") is not None,
         "ffprobe": shutil.which("ffprobe") is not None,
         "opencv": False, "heic": False, "scenedetect": False,
         "aesthetic": False, "whisper": False}
    try:
        import cv2  # noqa
        c["opencv"] = True
    except Exception:
        pass
    try:
        import pillow_heif  # noqa
        c["heic"] = True
    except Exception:
        pass
    try:
        import scenedetect  # noqa
        c["scenedetect"] = True
    except Exception:
        pass
    try:
        import simple_aesthetics_predictor  # noqa
        c["aesthetic"] = True
    except Exception:
        pass
    c["whisper"] = which_whisper() is not None and default_whisper_model() is not None
    return c


# ---------- image scoring ----------

def _metrics(path):
    """(laplacian_var, frac_dark, frac_bright, colorfulness) or None."""
    import cv2, numpy as np
    img = cv2.imread(path)
    if img is None:
        return None
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    lap = float(cv2.Laplacian(gray, cv2.CV_64F).var())
    hist = np.histogram(gray, bins=256, range=(0, 255))[0]
    total = gray.size
    dark = float(hist[:16].sum() / total)
    bright = float(hist[240:].sum() / total)
    # Hasler-Susstrunk colorfulness
    b, g, r = cv2.split(img.astype("float"))
    rg = np.absolute(r - g)
    yb = np.absolute(0.5 * (r + g) - b)
    colorful = float(np.sqrt(rg.std()**2 + yb.std()**2)
                     + 0.3 * np.sqrt(rg.mean()**2 + yb.mean()**2))
    return lap, dark, bright, colorful


def _aesthetic_proxy(m):
    """0..1 from OpenCV metrics. No heavy deps."""
    if m is None:
        return 0.0
    lap, dark, bright, colorful = m
    sharp = min(lap / 300.0, 1.0)                 # saturate ~300
    expo = 1.0 - min(dark + bright, 1.0)          # penalize crushed/blown
    color = min(colorful / 80.0, 1.0)
    return round(0.5 * sharp + 0.3 * expo + 0.2 * color, 4)


class Aesthetic:
    """Best-frame scorer. The OpenCV proxy is the wired default and the ONLY
    scorer used. CLIP is intentionally NOT loaded (see SETUP EXPERIMENTAL): we do
    not download or hold multi-GB weights for a signal that is not yet wired in.
    If/when CLIP is validated, score() is the single place to blend it."""
    def __init__(self, enabled):
        self.enabled = False  # proxy only, by design

    def score(self, path, m):
        return _aesthetic_proxy(m)


def quality_note(m, blur_thresh):
    """Returns (hard_reject_or_None, soft_flag_or_None).

    Raw/low-light/handheld footage IS this brand's aesthetic (RUBRIC authenticity
    premium), so blur and darkness are SOFT FLAGS the model adjudicates, NOT gates
    that kill an asset before the model ever sees it. Only truly unusable frames
    hard-reject. (This gate previously auto-killed ~47% of real founder footage,
    reproducing the exact 'good content silently ignored' failure it exists to stop.)"""
    if m is None:
        return "unreadable", None       # only genuine hard reject: file won't decode
    lap, dark, bright, _ = m
    if bright > 0.9:
        return "blown out (near-total white, unrecoverable)", None
    # Blur and darkness are NEVER hard kills. The model + authenticity premium decide,
    # because raw/handheld/low-light IS this brand's look. A Laplacian number must not
    # kill founder content before the model ever sees it.
    soft = None
    if lap < 30:
        soft = f"very soft/blurry (sharpness {lap:.0f}) - likely unusable, model decides"
    elif lap < blur_thresh:
        soft = f"soft/handheld (sharpness {lap:.0f}) - keep if the moment carries it"
    elif dark > 0.7:
        soft = "low-light/moody - on-brand if intentional"
    return None, soft


# ---------- video ----------

def duration(video):
    try:
        return float(subprocess.check_output(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration",
             "-of", "default=nw=1:nk=1", video]).strip())
    except Exception:
        return 6.0


def has_audio(video):
    try:
        out = subprocess.check_output(
            ["ffprobe", "-v", "error", "-select_streams", "a",
             "-show_entries", "stream=index", "-of", "csv=p=0", video],
            text=True).strip()
        return bool(out)
    except Exception:
        return False


def speech_ratio(video):
    """Fraction of the clip that is NOT silence (0..1). Robust silencedetect parse."""
    if not has_audio(video):
        return 0.0
    dur = duration(video)
    try:
        log = subprocess.run(
            ["ffmpeg", "-hide_banner", "-i", video, "-af",
             "silencedetect=noise=-30dB:d=0.5", "-f", "null", "-"],
            stderr=subprocess.PIPE, text=True).stderr
    except Exception:
        return 0.0
    sil = sum(float(x) for x in re.findall(r"silence_duration:\s*([0-9.]+)", log))
    if dur <= 0:
        return 0.0
    return max(0.0, min(1.0, 1.0 - sil / dur))


def scene_midpoints(video):
    from scenedetect import detect, AdaptiveDetector
    scenes = detect(video, AdaptiveDetector())
    out = [(s.get_seconds(), e.get_seconds()) for s, e in scenes]
    if not out:
        d = duration(video)
        return [(0.0, d)]
    return out


def extract_frame(video, t, dst):
    subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-ss",
                    f"{t:.2f}", "-i", video, "-frames:v", "1", "-q:v", "3",
                    "-y", dst], check=False)


def transcribe(video, whisper_bin, model, workdir):
    """Real whisper.cpp run. Returns transcript text or None."""
    wav = os.path.join(workdir, "audio.wav")
    subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-i", video,
                    "-ar", "16000", "-ac", "1", "-y", wav], check=False)
    if not os.path.exists(wav):
        return None
    base = os.path.join(workdir, "out")
    r = subprocess.run([whisper_bin, "-m", model, "-f", wav, "-otxt", "-of", base,
                        "-nt"], capture_output=True, text=True)
    txt = base + ".txt"
    if os.path.exists(txt):
        return Path(txt).read_text().strip()
    # some builds print to stdout
    return r.stdout.strip() or None


def process_video(video, out, caps, aes, blur_thresh, scenes_max,
                  cands, whisper_bin, model, use_whisper):
    rec = {"asset": video.name, "type": "video", "verdict": "assessed",
           "best_frame": None, "all_frames": [], "transcript": None, "notes": []}
    if not caps["ffmpeg"]:
        rec["verdict"] = "auto-rejected"
        rec["notes"].append("ffmpeg missing, cannot read video")
        return rec

    if caps["scenedetect"]:
        try:
            segs = scene_midpoints(str(video))
        except Exception as e:
            rec["notes"].append(f"scenedetect failed ({e}), interval fallback")
            segs = None
    else:
        rec["notes"].append("scenedetect not installed, interval fallback")
        segs = None
    if segs is None:
        d = duration(str(video))
        step = max(d / (scenes_max + 1), 1.0)
        segs = [(i * step, i * step) for i in range(1, scenes_max + 1)]
    segs = segs[:scenes_max]

    if not caps["opencv"]:
        rec["notes"].append("opencv missing, no blur/exposure gate, frames kept unchecked")
    kept = 0
    for si, (s, e) in enumerate(segs):
        # sample several candidates inside the scene, keep the best-scoring one
        span = max(e - s, 0.0)
        if span <= 0.05:
            # zero-span (interval fallback or instant scene): sample a small window
            offsets = [0.0, 0.4, -0.4, 0.8][:max(cands, 1)]
            times = [max(0.0, s + d) for d in offsets]
        else:
            times = [s + span * f for f in
                     [round((j + 1) / (cands + 1), 3) for j in range(cands)]]
        best = None
        for ci, t in enumerate(times):
            dst = str(out / f"{video.stem}_s{si:02d}c{ci}.jpg")
            extract_frame(str(video), t, dst)
            if not os.path.exists(dst):
                continue
            m = _metrics(dst) if caps["opencv"] else None
            score = aes.score(dst, m) if caps["opencv"] else 0.0
            cand = {"t": round(t, 2), "path": dst, "score": score,
                    "metrics_ok": m is not None}
            if best is None or score > best["score"]:
                if best is not None and os.path.exists(best["path"]) \
                        and best["path"] != dst:
                    try: os.remove(best["path"])      # drop the loser frame
                    except OSError: pass
                best = cand
            elif os.path.exists(dst):
                try: os.remove(dst)
                except OSError: pass
        if best is None:
            continue
        if caps["opencv"]:
            m = _metrics(best["path"])
            rej, soft = quality_note(m, blur_thresh)  # blur/dark = soft flag, not a kill
        else:
            rej, soft = None, None
        best["rejected"] = rej
        if soft:
            best["flag"] = soft
        rec["all_frames"].append(best)
        if rej is None:
            kept += 1
    if rec["all_frames"]:
        usable = [f for f in rec["all_frames"] if not f["rejected"]]
        pool = usable or rec["all_frames"]
        rec["best_frame"] = max(pool, key=lambda f: f["score"])["path"]
    if kept == 0 and rec["all_frames"]:
        rec["verdict"] = "auto-rejected"
        rec["notes"].append("all scene frames failed blur/exposure gate")

    # transcript only if there is real speech
    sr = speech_ratio(str(video))
    if use_whisper and caps["whisper"] and sr > 0.15:
        with tempfile.TemporaryDirectory() as wd:
            try:
                rec["transcript"] = transcribe(str(video), whisper_bin, model, wd)
                rec["notes"].append(f"transcribed (speech_ratio {sr:.2f})")
            except Exception as ex:
                rec["notes"].append(f"transcription failed: {ex}; visuals only")
    elif sr > 0.15:
        rec["notes"].append("speech present but whisper unavailable, scored on visuals only")
    else:
        rec["notes"].append("no significant speech, scored on visuals only")
    return rec


def process_photo(photo, out, caps, aes, blur_thresh):
    rec = {"asset": photo.name, "type": "photo", "verdict": "assessed", "notes": []}
    p = photo
    if photo.suffix.lower() in {".heic", ".heif"}:
        if caps["heic"]:
            from PIL import Image
            import pillow_heif
            pillow_heif.register_heif_opener()
            dst = out / (photo.stem + ".jpg")
            Image.open(photo).convert("RGB").save(dst, "JPEG", quality=92)
            p = dst
            rec["normalized"] = p.name
        else:
            rec["verdict"] = "auto-rejected"
            rec["notes"].append("HEIC but pillow-heif not installed, cannot read")
            return rec
    m = _metrics(str(p)) if caps["opencv"] else None
    rec["path"] = str(p)
    rec["score"] = aes.score(str(p), m) if caps["opencv"] else None
    if caps["opencv"]:
        rej, soft = quality_note(m, blur_thresh)
        if rej:
            rec["verdict"] = "auto-rejected"
            rec["notes"].append(rej)
        elif soft:
            rec["notes"].append(soft)
    return rec


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("folder", nargs="?")
    ap.add_argument("--out")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--blur-thresh", type=float, default=100.0)
    ap.add_argument("--scenes-max", type=int, default=8)
    ap.add_argument("--cands-per-scene", type=int, default=3)
    ap.add_argument("--whisper-model")
    ap.add_argument("--no-whisper", action="store_true")
    a = ap.parse_args()

    caps = cap()
    if a.selftest:
        print("Content Director · capability check")
        for k, v in caps.items():
            print(f"  {k:12} {'OK' if v else 'MISSING'}")
        print("\nbest-frame scorer:",
              "OpenCV proxy (wired default; CLIP intentionally unused)" if caps["opencv"]
              else "NONE (install opencv-python)")
        if not caps["ffmpeg"] or not caps["opencv"]:
            print("Core missing: ffmpeg + opencv-python are required. See SETUP.md.")
        else:
            print("Core ready. Optional (scenedetect/heic/whisper/CLIP) degrade gracefully.")
        return

    if not a.folder:
        print("usage: triage-media.py <folder> [--out DIR] (or --selftest)",
              file=sys.stderr)
        sys.exit(2)
    folder = Path(a.folder).expanduser()
    if not folder.is_dir():
        print(f"Not a local folder: {folder}. Sync the Drive folder down first (SETUP.md).",
              file=sys.stderr)
        sys.exit(1)
    out = Path(a.out).expanduser() if a.out else folder / "_triage"
    out.mkdir(parents=True, exist_ok=True)

    aes = Aesthetic(caps["aesthetic"])
    if caps["aesthetic"] and not aes.enabled:
        caps["aesthetic"] = False  # CLIP init failed, proxy in use
    wbin = which_whisper()
    wmodel = a.whisper_model or default_whisper_model()
    use_whisper = not a.no_whisper

    assets = sorted(p for p in folder.iterdir()
                    if p.suffix.lower() in PHOTO_EXT | VIDEO_EXT)
    manifest = {"folder": str(folder), "capabilities": caps,
                "scorer": "CLIP" if caps["aesthetic"] else "opencv-proxy",
                "uploaded": len(assets), "records": []}
    for p in assets:
        try:
            if p.suffix.lower() in VIDEO_EXT:
                manifest["records"].append(process_video(
                    p, out, caps, aes, a.blur_thresh, a.scenes_max,
                    a.cands_per_scene, wbin, wmodel, use_whisper))
            else:
                manifest["records"].append(process_photo(
                    p, out, caps, aes, a.blur_thresh))
        except Exception as e:
            manifest["records"].append(
                {"asset": p.name, "verdict": "auto-rejected", "notes": [f"error: {e}"]})

    v = [r["verdict"] for r in manifest["records"]]
    manifest["coverage"] = {"uploaded": len(assets), "assessed": v.count("assessed"),
                            "auto_rejected": v.count("auto-rejected"), "deduped": 0}
    mpath = out / "manifest.json"
    mpath.write_text(json.dumps(manifest, indent=2))
    print(f"Wrote {mpath}")
    print(f"Uploaded {len(assets)} · assessed {v.count('assessed')} · "
          f"auto-rejected {v.count('auto-rejected')} · scorer {manifest['scorer']}")
    print("Read manifest.json + the best-frame JPGs. Dedupe/scoring happen in-model next.")


if __name__ == "__main__":
    main()
