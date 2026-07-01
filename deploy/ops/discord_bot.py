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


def run_pipeline(fid):
    """Run the robust runner on a specific Drive folder id. The runner lists it (API
    key), downloads, triages, calls Claude, writes the sheet, and posts the digest."""
    env = dict(os.environ, MARGAUX_DAILY_FOLDER_ID=fid)
    subprocess.run(["bash", "deploy/ops/margaux-run.sh"], cwd=REPO, env=env,
                   timeout=1800)


@client.event
async def on_ready():
    print(f"Margaux online as {client.user}", flush=True)


@client.event
async def on_message(msg):
    if msg.author == client.user:
        return
    if ONLY_CHANNEL and str(msg.channel.id) != ONLY_CHANNEL:
        return
    text = (msg.content or "").lower()
    if "content delivery" not in text:
        return
    fid = folder_id(msg.content)
    if not fid:
        await msg.channel.send("Drop the Google Drive folder link along with "
                               "'content delivery' and I'll run it.")
        return
    await msg.channel.send("On it, going through your content now. A few minutes, "
                           "the digest will land here when it's done.")
    try:
        await asyncio.get_event_loop().run_in_executor(None, run_pipeline, fid)
        await msg.channel.send("Done, your picks are above.")
    except Exception as e:
        await msg.channel.send(f"Hit a snag: {e}")


if __name__ == "__main__":
    if not TOKEN:
        raise SystemExit("set DISCORD_BOT_TOKEN in .env.margaux")
    client.run(TOKEN)
