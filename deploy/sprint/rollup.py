#!/usr/bin/env python3
"""
rollup.py · the Command Center's status roll-up for the Margaux build sprint.

Cross-platform (stdlib only). One call:
  1. git pull (so it sees every contractor's pushed log)
  2. reads the last status line from each logs/TERMINAL-WS<n>-LOG.md
  3. posts ONE consolidated status to Discord #build-updates (Kailin)
  4. appends the rollup to logs/COMMAND-CENTER-LOG.md

Usage:
  python deploy/sprint/rollup.py [--no-pull]

Env: DISCORD_BUILD_WEBHOOK  (Kailin's channel)
Run it on a cadence, or after each contractor milestone.
"""
import argparse, glob, json, os, re, subprocess, sys, urllib.request
from datetime import datetime, timezone

WS_ORDER = ["WS0", "WS1", "WS2", "WS3", "WS4", "WS5", "WS6", "WS7"]


def post(webhook, content):
    if not webhook:
        print("  DISCORD_BUILD_WEBHOOK unset, printing only", file=sys.stderr)
        print(content)
        return
    try:
        req = urllib.request.Request(
            webhook, data=json.dumps({"content": content}).encode(),
            headers={"Content-Type": "application/json"})
        urllib.request.urlopen(req, timeout=15)
    except Exception as e:
        print(f"  discord post failed: {e}", file=sys.stderr)


def root():
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "--show-toplevel"], text=True).strip()
    except Exception:
        return os.getcwd()


def last_line(path):
    try:
        lines = [l.strip() for l in open(path) if l.strip().startswith("- ")]
        return lines[-1] if lines else None
    except Exception:
        return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-pull", action="store_true")
    a = ap.parse_args()
    r = root()

    if not a.no_pull:
        subprocess.run(["git", "-C", r, "pull", "-q"], check=False)

    logdir = os.path.join(r, "logs")
    rows, blockers = [], []
    for ws in WS_ORDER:
        p = os.path.join(logdir, f"TERMINAL-{ws}-LOG.md")
        ll = last_line(p)
        if not ll:
            rows.append(f"{ws}: ⚪ not started")
            continue
        pct = re.search(r"·\s*(\d+)%", ll)
        emoji = re.search(r"·\s*(\S+)\s+\w+\s*·", ll)
        rows.append(f"{ws}: {ll.split('· ',1)[-1] if '· ' in ll else ll}")
        if "BLOCKER:" in ll:
            blockers.append(f"{ws}: {ll.split('BLOCKER:',1)[1].strip()}")

    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    body = f"**MARGAUX BUILD · Command Center rollup · {ts}**\n" + "\n".join(rows)
    if blockers:
        body += "\n\n🔴 **BLOCKERS NEEDING KAILIN:**\n" + "\n".join(blockers)

    post(os.environ.get("DISCORD_BUILD_WEBHOOK"), body)

    cc = os.path.join(logdir, "COMMAND-CENTER-LOG.md")
    os.makedirs(logdir, exist_ok=True)
    with open(cc, "a") as f:
        f.write(f"\n### rollup {ts}\n" + "\n".join(f"- {x}" for x in rows) + "\n")
    print("rollup posted + logged")


if __name__ == "__main__":
    main()
