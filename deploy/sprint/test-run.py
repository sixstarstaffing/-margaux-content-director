#!/usr/bin/env python3
"""
test-run.py · the minimal Margaux worker, for a real proof-run on a real folder.

Pipeline: triage-media.py extracts best frames -> we send those frames + the brain
(SKILL.md + rubric/routing/hooks/voice) to Claude -> Claude (as Margaux) returns the
daily routing sheet. This is her actual judgment on real footage, printed as text.

Run on the VPS (has ffmpeg, python, disk). Needs ANTHROPIC_API_KEY in the env.

Usage:
  python deploy/sprint/test-run.py --folder ./content [--model claude-sonnet-5] \
      [--max-images 24] [--out routing-sheet.md]
"""
import argparse, base64, io, json, os, subprocess, sys
from pathlib import Path

BRAIN_FILES = ["SKILL.md", "RUBRIC.md", "ROUTING-TREE.md", "HOOKS.md",
               "PERSONAL-BRAND.md", "FORMATS.md", "BOARDS.md", "OUTPUT-TEMPLATE.md"]


def load_brain(root):
    parts = []
    for f in BRAIN_FILES:
        p = root / f
        if p.exists():
            parts.append(f"\n\n===== {f} =====\n" + p.read_text())
    return "".join(parts)


def run_triage(root, folder):
    """Run the real extraction pipeline; returns the manifest dict."""
    script = root / "scripts" / "triage-media.py"
    out = Path(folder) / "_triage"
    subprocess.run([sys.executable, str(script), str(folder), "--out", str(out)],
                   check=False)
    mpath = out / "manifest.json"
    if not mpath.exists():
        print("triage produced no manifest; aborting", file=sys.stderr)
        sys.exit(1)
    return json.loads(mpath.read_text())


def frame_for(rec):
    """Best small JPG to show Claude for this asset."""
    if rec.get("type") == "video":
        return rec.get("best_frame")
    return rec.get("path")  # photo (HEIC already normalized to jpg by triage)


def b64(path, max_px=1024):
    """Downscale to <=max_px long edge + re-encode JPEG, so the API request stays
    small (Claude resizes internally anyway; we just avoid the 32MB request cap)."""
    from PIL import Image
    img = Image.open(path).convert("RGB")
    img.thumbnail((max_px, max_px))
    buf = io.BytesIO()
    img.save(buf, "JPEG", quality=80)
    return base64.standard_b64encode(buf.getvalue()).decode()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--folder", required=True)
    ap.add_argument("--model", default="claude-sonnet-5")
    ap.add_argument("--max-images", type=int, default=16)
    ap.add_argument("--out", default="routing-sheet.md")
    a = ap.parse_args()

    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("Set ANTHROPIC_API_KEY in the env first.", file=sys.stderr); sys.exit(2)
    try:
        import anthropic
    except ImportError:
        print("pip install anthropic first.", file=sys.stderr); sys.exit(2)

    root = Path(__file__).resolve().parents[2]  # repo root
    brain = load_brain(root)
    manifest = run_triage(root, a.folder)
    records = manifest.get("records", [])

    # gather assets that have a usable frame, cap to keep the call sane
    assets = []
    for r in records:
        fp = frame_for(r)
        if fp and os.path.exists(fp):
            assets.append((r, fp))
    dropped = max(0, len(assets) - a.max_images)
    assets = assets[:a.max_images]

    # build the multimodal message: filename label + its frame, interleaved
    content = [{"type": "text", "text":
        "You are MARGAUX, the Content Director. Below are the best frames from a real "
        "day of Kailin's footage (the 6/23 batch). Using your brain (rubric, routing, "
        "hooks, voice, boards) produce the ONE daily routing sheet per OUTPUT-TEMPLATE.md. "
        "Route personal-first. Be honest: reject what is weak, and for anything held, say "
        "why. This is a real test of your judgment. Filenames precede each frame."}]
    for r, fp in assets:
        label = f"\n--- {r.get('asset')} ({r.get('type')}) verdict-so-far={r.get('verdict')} ---"
        content.append({"type": "text", "text": label})
        content.append({"type": "image", "source": {
            "type": "base64", "media_type": "image/jpeg", "data": b64(fp)}})
    if dropped:
        content.append({"type": "text", "text":
            f"\n(NOTE: {dropped} more assets not shown due to the image cap; mention that "
            "coverage was capped for this test run.)"})

    print(f"sending {len(assets)} frames to {a.model} as Margaux's brain...", file=sys.stderr)
    client = anthropic.Anthropic()
    kwargs = dict(
        model=a.model, max_tokens=12000,
        system="You are MARGAUX, a content director. Follow this brain exactly:\n" + brain,
        messages=[{"role": "user", "content": content}])
    try:  # sonnet-5 defaults thinking ON and it eats the whole budget; turn it off
        msg = client.messages.create(thinking={"type": "disabled"}, **kwargs)
    except Exception:
        msg = client.messages.create(**kwargs)  # model without a thinking param
    blocks = [getattr(b, "type", "?") for b in msg.content]
    print(f"[api] stop_reason={msg.stop_reason} blocks={blocks} usage={msg.usage}",
          file=sys.stderr)
    sheet = "".join(getattr(b, "text", "") for b in msg.content
                    if getattr(b, "type", "") == "text")
    if not sheet.strip():
        print("[api] EMPTY text returned. Raw content repr (first 2000 chars):",
              file=sys.stderr)
        print(repr(msg.content)[:2000], file=sys.stderr)

    Path(a.out).write_text(sheet)
    print("\n" + "=" * 70 + "\nMARGAUX ROUTING SHEET (real run)\n" + "=" * 70 + "\n")
    print(sheet)
    print("\n" + "=" * 70)
    print(f"saved -> {a.out} · assets shown {len(assets)} · dropped {dropped}", file=sys.stderr)


if __name__ == "__main__":
    main()
