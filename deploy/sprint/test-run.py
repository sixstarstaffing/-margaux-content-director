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

# KNOWLEDGE.md first (Sevyn method + in-voice playbook = the expertise). Dropped the
# ops-heavy SKILL.md and BOARDS.md from the prompt (they're orchestration, not judgment)
# per the prompt review, so she's smarter AND leaner.
BRAIN_FILES = ["KNOWLEDGE.md", "RUBRIC.md", "ROUTING-TREE.md", "HOOKS.md",
               "PERSONAL-BRAND.md", "FORMATS.md", "OUTPUT-TEMPLATE.md"]


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


def load_notes(folder, root):
    """Read the creator's one-line notes (who/what per clip) and map file-number -> note.
    Matches Kailin's natural style: lines like '5054 Tnaryl in the car with plated supplies'
    or '5054: ...' or '5054 - ...'. The number is matched as a substring of the filename.
    Looks for notes.txt/notes.md in the folder, else deploy/sprint/notes.txt in the repo."""
    import re
    text = ""
    for c in (os.path.join(folder, "notes.txt"), os.path.join(folder, "notes.md"),
              os.path.join(root, "deploy", "sprint", "notes.txt")):
        if os.path.exists(c):
            text = open(c).read()
            break
    notes = {}
    for line in text.splitlines():
        line = line.strip().lstrip("*#-•> \t").strip()
        m = re.search(r"\b(\d{3,5})\b", line)
        if not m:
            continue
        key = m.group(1)
        note = line[m.end():].lstrip(" :.-–—\t").strip()
        if note:
            notes[key] = note
    return notes


def b64(path, max_px=768):
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
    ap.add_argument("--max-images", type=int, default=48)  # full-folder coverage
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
    notes = load_notes(a.folder, str(root))     # creator's who/what notes (ground truth)
    if notes:
        print(f"loaded {len(notes)} creator notes", file=sys.stderr)
    manifest = run_triage(root, a.folder)
    records = manifest.get("records", [])

    # gather assets that have a usable frame, then send the BEST max_images (not the
    # first N): rank assessed-over-rejected, then by score, so the cap never silently
    # drops a gem just because of file order.
    ranked = []
    for r in records:
        fp = frame_for(r)
        if not (fp and os.path.exists(fp)):
            continue
        if r.get("type") == "video" and r.get("all_frames"):
            sc = max((f.get("score", 0) or 0) for f in r["all_frames"])
        else:
            sc = r.get("score") or 0
        rank = (0 if r.get("verdict") == "auto-rejected" else 1, sc)
        ranked.append((rank, r, fp))
    ranked.sort(key=lambda x: x[0], reverse=True)
    dropped = max(0, len(ranked) - a.max_images)
    assets = [(r, fp) for _, r, fp in ranked[:a.max_images]]

    # build the multimodal message: filename label + its frame, interleaved
    content = [{"type": "text", "text":
        "You are MARGAUX, the Content Director. Below are best frames from one real day of "
        "Kailin's raw footage. Produce the ONE daily routing sheet per OUTPUT-TEMPLATE, using "
        "your KNOWLEDGE (Sevyn method + Kailin's voice), rubric, and routing rules. Route "
        "personal-first. Reject what is weak; for anything held, say why.\n"
        "IMPORTANT: each image is a single best-frame STILL from a video, you cannot see motion "
        "or hear audio. Do NOT invent dialogue, on-screen text, or a reveal you can't see. If a "
        "hook depends on unseen footage, mark it an assumption / shotlist item, do not assert it.\n"
        "A 'CREATOR NOTE' next to a clip is Kailin telling you exactly who/what is in it, that is "
        "GROUND TRUTH: use it to route and write accurate hooks, and never contradict it."}]
    for r, fp in assets:
        label = f"\n--- {r.get('asset')} ({r.get('type')}) ---"
        note = next((v for k, v in notes.items() if k in r.get("asset", "")), None)
        if note:
            label += f"\n  CREATOR NOTE (ground truth): {note}"
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
        model=a.model, max_tokens=16000,
        system="You are MARGAUX, a content director. Follow this brain exactly:\n" + brain,
        messages=[{"role": "user", "content": content}])
    try:  # sonnet-5 defaults thinking ON and it eats the whole budget; turn it off
        msg = client.messages.create(thinking={"type": "disabled"}, **kwargs)
    except TypeError:  # only if the SDK rejects the kwarg; do NOT swallow real API errors
        msg = client.messages.create(**kwargs)
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
    if not sheet.strip():
        print("FAILED: empty sheet (see [api] line above)", file=sys.stderr)
        sys.exit(3)  # never report success on empty output


if __name__ == "__main__":
    main()
