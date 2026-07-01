#!/usr/bin/env python3
"""
report.py · a contractor terminal's status reporter for the Margaux build sprint.

Cross-platform (stdlib only, runs on the PC). One call:
  1. appends a timestamped line to logs/TERMINAL-WS<n>-LOG.md (this terminal's own log)
  2. posts to Discord #build-updates  (Kailin watches)  AND  the command-center channel
  3. optionally git commit+push this terminal's log so Command Center can roll it up

Usage:
  python deploy/sprint/report.py --ws WS2 --status running --pct 40 \
      --msg "worker skeleton up, wiring triage-media" [--blocker "..."] [--push]

Env (from the shared secret store, never hardcode):
  DISCORD_BUILD_WEBHOOK            Kailin's #build-updates channel
  DISCORD_COMMAND_CENTER_WEBHOOK  command-center aggregation channel
"""
import argparse, json, os, subprocess, sys, urllib.request
from datetime import datetime, timezone

STATUS_EMOJI = {"started": "🟢", "running": "🔵", "milestone": "✅",
                "blocked": "🔴", "done": "🏁", "failed": "⚠️"}


def post(webhook, content):
    if not webhook:
        return False
    try:
        req = urllib.request.Request(
            webhook, data=json.dumps({"content": content}).encode(),
            headers={"Content-Type": "application/json"})
        urllib.request.urlopen(req, timeout=15)
        return True
    except Exception as e:
        print(f"  discord post failed: {e}", file=sys.stderr)
        return False


def repo_root():
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "--show-toplevel"], text=True).strip()
    except Exception:
        return os.getcwd()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ws", required=True, help="WS0..WS7 or CC")
    ap.add_argument("--status", required=True, choices=list(STATUS_EMOJI))
    ap.add_argument("--pct", type=int, default=0)
    ap.add_argument("--msg", required=True)
    ap.add_argument("--blocker", default="")
    ap.add_argument("--push", action="store_true", help="commit+push this log")
    a = ap.parse_args()

    root = repo_root()
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    emoji = STATUS_EMOJI[a.status]
    line = f"- {ts} · {emoji} {a.status} · {a.pct}% · {a.msg}"
    if a.blocker:
        line += f"  ·  BLOCKER: {a.blocker}"

    # 1) append to this terminal's own log (no cross-terminal write = no conflicts)
    logdir = os.path.join(root, "logs")
    os.makedirs(logdir, exist_ok=True)
    logfile = os.path.join(logdir, f"TERMINAL-{a.ws}-LOG.md")
    with open(logfile, "a") as f:
        f.write(line + "\n")
    print(f"logged -> {logfile}")

    # 2) Discord: to Kailin AND relay to Command Center
    card = (f"**[{a.ws}] {emoji} {a.status}** ({a.pct}%)\n{a.msg}"
            + (f"\n🔴 **BLOCKER:** {a.blocker}" if a.blocker else ""))
    to_kailin = post(os.environ.get("DISCORD_BUILD_WEBHOOK"), card)
    to_cc = post(os.environ.get("DISCORD_COMMAND_CENTER_WEBHOOK"), card)
    print(f"discord -> kailin:{to_kailin} command-center:{to_cc}")

    # 3) optionally push so Command Center's rollup can read it across machines
    if a.push:
        try:
            subprocess.run(["git", "-C", root, "add", logfile], check=True)
            subprocess.run(["git", "-C", root, "commit", "-q", "-m",
                            f"{a.ws} {a.status} {a.pct}%: {a.msg[:60]}"], check=True)
            subprocess.run(["git", "-C", root, "push", "-q"], check=True)
            print("pushed log")
        except Exception as e:
            print(f"  push skipped/failed: {e}", file=sys.stderr)


if __name__ == "__main__":
    main()
