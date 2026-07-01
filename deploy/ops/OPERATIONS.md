# Margaux · Operations (so the manual pain never happens again)

Everything that broke on 2026-07-01 (stale git, dropped SSH killing runs, wrong host/container, empty pasted key, stale files, re-downloads) is fixed by ONE runner: `deploy/ops/margaux-run.sh`. It is idempotent, disconnect-safe, and cron-safe.

## The fixed home (stop the host/container confusion)
Margaux lives INSIDE the container, at `/root/margaux-test`.
- Public SSH lands you on the **host** `srv1770791`. To reach Margaux, step into the container:
  ```
  docker exec -it 9d07c76c04ac bash
  cd /root/margaux-test
  ```
  (If that id changes, `docker ps` lists containers.)

## One-time setup (do these ONCE, then never again)
1. Store the API key in a file so it is never pasted again:
   ```
   printf 'ANTHROPIC_API_KEY=%s\n' 'sk-ant-...' > /root/margaux-test/.env.margaux
   chmod 600 /root/margaux-test/.env.margaux
   ```
2. (Optional) a Discord webhook so the sheet comes to you, not the terminal:
   ```
   printf 'DISCORD_BUILD_WEBHOOK=%s\n' 'https://discord.com/api/webhooks/...' >> /root/margaux-test/.env.margaux
   ```
3. (Optional) let Claude drive it directly so you never relay pastes again: add Claude's
   public key to the **host** root (`srv1770791`), not just the container, so it can
   `ssh root@2.24.196.176` then `docker exec` in. That kills the paste-loop.

## Daily run (by hand) · one command, survives disconnects
```
cd /root/margaux-test && nohup bash deploy/ops/margaux-run.sh deploy/sprint/test-file-ids.txt >/dev/null 2>&1 &
```
Then read the newest sheet (no stale confusion, they are timestamped):
```
ls -t sheets | head -1        # newest file name
cat sheets/$(ls -t sheets | head -1)
```

## Daily run (automatic) · zero commands
Answer to "who runs her daily and where": **cron, on the VPS.** Install once:
```
( crontab -l 2>/dev/null; echo '30 6 * * * cd /root/margaux-test && bash deploy/ops/margaux-run.sh deploy/sprint/test-file-ids.txt >> /root/margaux-test/cron.log 2>&1' ) | crontab -
```
That runs her every day at 6:30am, writes a timestamped sheet, and (if the webhook is set) pings you in Discord. No terminal, no pasting, no dropped connections.

## Per-folder input
Point her at a different day by giving a different id list (one `id filename` per line).
Generate one from any shared Drive folder and pass it as the argument. The real product
(WS2 worker) will take a Drive LINK and build this list itself via rclone; this file-id
list is the interim while that is unbuilt.

## Why this fixes each failure
- **Stale git** → `git fetch && reset --hard` every run (never behind again).
- **Dropped SSH kills run** → `nohup`/cron: it runs detached, disconnect can't touch it.
- **Host vs container** → fixed home + documented `docker exec` entry.
- **Empty pasted key** → stored once in `.env.margaux`, verified by the runner, never pasted.
- **Stale output** → every sheet is timestamped in `sheets/`, newest is obvious.
- **Re-downloading 2.4GB** → skips files already in `flat/`.
