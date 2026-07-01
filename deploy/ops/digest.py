#!/usr/bin/env python3
"""
digest.py · turn a full routing sheet into a 10-second digest for Kailin and post it
to Discord. The full sheet is for the editor/GiGi; Kailin gets the short version.

Usage: python deploy/ops/digest.py <sheet.md>
Env:   DISCORD_BUILD_WEBHOOK (where the digest goes; prints if unset)
"""
import json, os, re, sys, urllib.request

sheet = open(sys.argv[1]).read() if len(sys.argv) > 1 else sys.stdin.read()

# day header ("# Content Director · <date> · <n> days to July 30")
hdr = re.search(r"^#\s*Content Director\s*·\s*(.+)$", sheet, re.M)
header = hdr.group(1).strip() if hdr else "today"

# "Do this first"
m = re.search(r"##\s*Do this first\s*(.+?)(?:\n##|\Z)", sheet, re.S)
first = re.sub(r"\s+", " ", m.group(1)).strip()[:350] if m else ""

# ready posts: "### N. Title ..." + its on-screen hook
posts = []
for block in re.split(r"\n###\s+", sheet):
    tm = re.match(r"\d+\.\s*(.+)", block)
    if not tm:
        continue
    title = re.split(r"·|\(", tm.group(1))[0].strip()[:55]
    hk = re.search(r"Hook \(on-screen\):\*{0,2}\s*[\"“]?([^\"”\n]+)", block)
    hook = hk.group(1).strip(' "*·') if hk else ""
    posts.append((title, hook))

lines = [f"**Margaux · picks for {header}**", "",
         f"▶️ **DO FIRST:** {first}" if first else ""]
if posts:
    lines += ["", f"**Ready to post ({len(posts)}):**"]
    for i, (t, h) in enumerate(posts[:8], 1):
        lines.append(f"{i}. {t}" + (f'  ·  "{h}"' if h else ""))
lines += ["", "_reply 'full' for captions + the editor handoff_"]
msg = "\n".join(x for x in lines if x is not None)[:1900]

wh = os.environ.get("DISCORD_BUILD_WEBHOOK", "").strip()
if wh:
    try:
        urllib.request.urlopen(urllib.request.Request(
            wh, data=json.dumps({"content": msg}).encode(),
            headers={"Content-Type": "application/json",
                     "User-Agent": "Margaux/1.0 (content-director)"}), timeout=15)
        print("digest posted to Discord")
    except Exception as e:
        print(f"digest post failed: {e}\n{msg}")
else:
    print(msg)
