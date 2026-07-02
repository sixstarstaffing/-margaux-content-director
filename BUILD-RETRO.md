# Margaux · Build Retrospective (hard scrutiny, so it never happens again)

**Written 2026-07-02.** No victory lap. What actually slowed this build, why, and the
rule that prevents each one next time. Feeds the AI-Employee Playbook.

## Timeline (honest)
- **2026-06-30** — brain built as a skill; 3-board review (v1 **58** → **94**); voice
  seeded; deploy plan written (**41 → 96**).
- **2026-07-01** — hosted on the Hermes VPS; validated on real footage; ops hardened;
  Discord digest; the two terminal-free triggers (folder cron + Discord bot); validated
  end-to-end from Discord on a real 34-clip folder.

Elapsed ~2 days. But most of the *lost* time was not the hard AI work, it was the boring
stuff below. That is the lesson.

## Biggest blockers (ranked by time lost) and the fix
1. **Built on the personal Mac first (should have been hosted day one).** Disk full
   (ENOSPC), no ffmpeg/rclone, a corrupt family-photo zip detour. Hours gone before any
   real triage ran. → **RULE: any agent that processes media/large files is hosted-first.
   Never make the personal machine the worker.**
2. **Credentials were the real critical path, and I treated them as a footnote.** Empty
   pasted API key; Google API-key creation confusion; Discord "token" that was actually
   the App ID + Public Key; the test folder not shared publicly. Each cost a round-trip.
   → **RULE: front-load credentials. Give exact click-by-click (or Claude-in-Chrome)
   prompts, and VERIFY each with a live test call before moving on. Name the exact thing
   ("bot token has dots, from Bot > Reset Token", not "the token").**
3. **I declared "shipped" while the trigger still needed this terminal open.** Kailin
   caught it: "I won't always have this terminal open." The engine worked; her real
   workflow did not. → **RULE: "done" is defined from the USER's seat, unattended. If it
   only works while a builder terminal is open, it is not shipped.**
4. **The bug that recreated the exact failure we were fixing.** The blur gate auto-killed
   47% of raw footage, i.e. good content silently dropped, the 6/23 problem reborn in
   code. → **RULE: test against REAL footage + Kailin's blind ratings, not synthetic.
   The failure you are fixing is the first thing to regression-test.**
5. **Tested the engine, not the user's real path.** The bot processed the wrong folder
   (runner re-sourced .env and clobbered the folder the bot passed) and posted the digest
   to the wrong channel (old build webhook, not where she typed). Both only surfaced when
   Kailin actually posted in Discord. → **RULE: test the literal user action (post in
   Discord), end to end, before calling it live. Env precedence and "deliver where they
   asked" are not details.**
6. **Stale git / host-vs-container confusion.** `git pull` sat 6 commits behind for an
   hour; SSH lands on the host, the repo is in a container. → **RULE (already coded): the
   runner does `git fetch && reset --hard` every run; the exact `docker exec` entry is in
   OPERATIONS.md.**
7. **False "done" messages.** The bot said "picks are above" when there were none. →
   **RULE: never report success without verifying the output artifact exists.**
8. **Speed.** PySceneDetect on 4K + whisper on big clips was slow. → **RULE (fixed):
   size-gate expensive steps; degrade gracefully and say what was skipped.**

## The one meta-lesson
The AI work (triage brain, voice, routing) went fine. **The build was slowed almost
entirely by plumbing: where it runs, credentials, and defining "done" honestly.** Next
AI employee: hosted-first, credentials-first, and "done" measured from the user opening
Discord with every builder terminal closed.

## What Margaux can and cannot do (so expectations are set)
- **CAN, unattended, no terminal:** triage a Drive folder and post picks to Discord
  (folder cron OR "content delivery" + link), and upload the full sheet on "full".
- **CANNOT:** fix or change herself, rotate keys, restart after a host rebuild beyond the
  watchdog, or do anything outside content triage. Those need a terminal with VPS access.

## Still open (tracked, not blocking)
- Rotate leaked keys (Anthropic, Blotato, VPS password).
- WS6 Supabase export so picks land in the BrandForge portal, not just Discord.
- Zero-touch across a host-container rebuild (systemd/compose service, not just cron
  watchdog).
