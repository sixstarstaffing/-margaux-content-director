#!/usr/bin/env bash
# start-bot.sh · run Margaux's Discord bot as a persistent background service.
cd "${MARGAUX_REPO:-/root/margaux-test}" || exit 1
[ -f .env.margaux ] && { set -a; . ./.env.margaux; set +a; }
[ -z "${DISCORD_BOT_TOKEN:-}" ] && { echo "set DISCORD_BOT_TOKEN in .env.margaux first"; exit 2; }
[ -d .venv ] || python3 -m venv .venv
. .venv/bin/activate
python -c "import discord" 2>/dev/null || pip install -q "discord.py"
pkill -f "[d]iscord_bot.py" 2>/dev/null; sleep 1
nohup python deploy/ops/discord_bot.py > bot.log 2>&1 &
sleep 3
echo "bot started (pid $!)"; tail -3 bot.log
