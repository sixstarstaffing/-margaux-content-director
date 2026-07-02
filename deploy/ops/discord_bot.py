#!/usr/bin/env python3
"""
discord_bot.py · Margaux's Discord bot (OPTION B). Lives on the VPS, listens in the
channel, and when Kailin posts a Drive FOLDER link + "content delivery", it runs the
pipeline on that folder and the digest posts back (via the webhook the runner uses).

So Kailin never needs a terminal: drop link + "content delivery" in Discord, get the
digest in Discord.

Env (from .env.margaux):
  DISCORD_BOT_TOKEN   the bot token (Discord Developer Portal)
  DISCORD_CHANNEL_ID  optional, restrict to one channel
  MARGAUX_REPO        default /root/margaux-test
  (plus GDRIVE_API_KEY + DISCORD_BUILD_WEBHOOK that the runner needs)

Run: python deploy/ops/discord_bot.py   (as a service, see run below)
"""
import asyncio, os, re, subprocess
import discord

TOKEN = os.environ.get("DISCORD_BOT_TOKEN", "").strip()
ONLY_CHANNEL = os.environ.get("DISCORD_CHANNEL_ID", "").strip()
REPO = os.environ.get("MARGAUX_REPO", "/root/margaux-test")

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)


def folder_id(text):
    m = re.search(r"/folders/([A-Za-z0-9_-]+)", text) or re.search(r"[?&]id=([A-Za-z0-9_-]+)", text)
    return m.group(1) if m else None


def newest_sheet():
    d = os.path.join(REPO, "sheets")
    fs = [os.path.join(d, f) for f in os.listdir(d)] if os.path.isdir(d) else []
    return max(fs, key=os.path.getmtime) if fs else None


def run_pipeline(fid):
    """Run the runner on the folder Kailin just posted, then return the digest TEXT so
    the bot can post it into this channel. MARGAUX_SKIP_WEBHOOK stops the runner from
    also firing the separate build webhook (wrong channel). Returns None if the folder
    had no new postable media."""
    before = newest_sheet()
    env = dict(os.environ, MARGAUX_DAILY_FOLDER_ID=fid, MARGAUX_SKIP_WEBHOOK="1")
    subprocess.run(["bash", "deploy/ops/margaux-run.sh"], cwd=REPO, env=env, timeout=1800)
    sheet = newest_sheet()
    if not sheet or sheet == before:
        return None  # empty folder / nothing new -> honest "nothing" message
    out = subprocess.run(["python", "deploy/ops/digest.py", "--text", sheet], cwd=REPO,
                         capture_output=True, text=True, timeout=60)
    return (out.stdout or "").strip() or None


@client.event
async def on_ready():
    print(f"Margaux online as {client.user}", flush=True)


@client.event
async def on_message(msg):
    if msg.author == client.user:
        return
    if ONLY_CHANNEL and str(msg.channel.id) != ONLY_CHANNEL:
        return
    text = (msg.content or "").strip().lower()

    # "full" -> upload the full routing sheet (captions + editor handoff), the thing
    # the digest promises. Kept short so a normal sentence doesn't trigger it.
    if text in ("full", "reply full", "margaux full", "@margaux full") or \
       (text.startswith("full") and len(text) <= 8):
        sheet = newest_sheet()
        if sheet:
            await msg.channel.send(
                "Full routing sheet, captions + editor handoff:",
                file=discord.File(sheet, filename="margaux-routing-sheet.md"))
        else:
            await msg.channel.send("No sheet yet, send a folder with 'content delivery' first.")
        return

    if "content delivery" not in text:
        return
    fid = folder_id(msg.content)
    if not fid:
        await msg.channel.send("Drop the Google Drive folder link along with "
                               "'content delivery' and I'll run it.")
        return
    await msg.channel.send("On it, going through your content now. A few minutes, "
                           "the digest will land right here when it's done.")
    try:
        digest = await asyncio.get_event_loop().run_in_executor(None, run_pipeline, fid)
    except Exception as e:
        await msg.channel.send(f"Hit a snag: {e}")
        return
    if digest:
        for i in range(0, len(digest), 1900):
            await msg.channel.send(digest[i:i + 1900])
    else:
        await msg.channel.send("Went through that folder but didn't find new postable "
                               "photos/videos (looks empty or just docs). Drop the clips "
                               "in and post the link again.")


if __name__ == "__main__":
    if not TOKEN:
        raise SystemExit("set DISCORD_BOT_TOKEN in .env.margaux")
    client.run(TOKEN)
