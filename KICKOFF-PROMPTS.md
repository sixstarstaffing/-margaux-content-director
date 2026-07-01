# Margaux Build Sprint · 10 terminal kickoff prompts

One paste per terminal. Open 10 Claude Code terminals on the PC, paste the matching block. WS0 + WS1 run first (critical path); WS2-WS7 wait until Command Center announces WS1 is frozen.

Clone note: the repo name has a leading dash, so we clone into a plain folder `margaux`.

---

## T1 · WS0 · Secrets (start now)
```
You are contractor terminal T1 (WS0, Secrets) on the Margaux build sprint.
1. git clone https://github.com/sixstarstaffing/-margaux-content-director.git margaux && cd margaux
2. Read BUILD-SPRINT.md and deploy/sprint/TERMINAL-BOOTSTRAP.md. RULE #1: never use a file on Kailin's Mac; everything is in this clone.
3. WS0: ROTATE the leaked Blotato key first (revoke old, mint new). Provision the .env on the Hostinger Hermes VPS from deploy/.env.template: Anthropic key, Supabase service+anon keys, Discord bot token + webhooks, rclone Drive headless OAuth, WORKER_SHARED_SECRET, N8N_CALLBACK_URL. Store in n8n credentials + Supabase Vault. Never commit .env, never a Mac file.
4. Acceptance: no secret in git; a fresh terminal can get TEST creds from the shared store without a Mac file.
5. Report: python deploy/sprint/report.py --ws WS0 --status started --pct 0 --msg "rotating Blotato + provisioning secrets" --push
Report milestone/blocked/done as you go.
```

## T2 · WS1 · Supabase schema (start now, critical path)
```
You are contractor terminal T2 (WS1, Supabase schema) on the Margaux build sprint.
1. git clone https://github.com/sixstarstaffing/-margaux-content-director.git margaux && cd margaux
2. Read BUILD-SPRINT.md + deploy/sprint/TERMINAL-BOOTSTRAP.md. RULE #1: no Mac files.
3. WS1: apply deploy/schema/001_init.sql then 002_rls.sql to the Supabase project. Create the Storage bucket margaux-frames. Verify enums, FKs, indexes, idempotency uniques, and RLS all apply clean. This schema is a FROZEN contract; once merged, tell Command Center so downstream lanes can start.
4. Acceptance: migration applies clean on a fresh Supabase; frozen + versioned.
5. Report: python deploy/sprint/report.py --ws WS1 --status started --pct 0 --msg "applying schema" --push
Report milestone/blocked/done. Announce FROZEN when done.
```

## T3 · WS2 · VPS worker (wait for WS0+WS1)
```
You are contractor terminal T3 (WS2, VPS worker) on the Margaux build sprint. Do NOT start until Command Center says WS0 secrets + WS1 schema are ready.
1. git clone https://github.com/sixstarstaffing/-margaux-content-director.git margaux && cd margaux
2. Read BUILD-SPRINT.md, MARGAUX-DEPLOY.md, deploy/API-CONTRACTS.md. RULE #1: no Mac files.
3. WS2: on Hermes, install ffmpeg/opencv/pillow-heif/scenedetect/rclone + build whisper.cpp (or add a faster-whisper branch to scripts/triage-media.py). Build the worker service exposing POST /jobs, GET /jobs/{id}, cancel per deploy/API-CONTRACTS.md: sync-drive.sh -> triage-media.py -> Claude API using SKILL.md as the system prompt -> write Supabase -> delete pulled media. Add heartbeat + restart reconciler + retry + disk cap (MARGAUX_WORKDIR / MARGAUX_DISK_BUDGET_GB / MARGAUX_MAX_CONCURRENT_JOBS).
4. Acceptance: python scripts/triage-media.py --selftest is green on Hermes; one real end-to-end job on a test Drive folder writes assets+verdicts to Supabase.
5. Report: python deploy/sprint/report.py --ws WS2 --status started --pct 0 --msg "worker skeleton" --push
```

## T4 · WS3 · n8n flows (wait for WS1 + WS2 API)
```
You are contractor terminal T4 (WS3, n8n) on the Margaux build sprint. Wait for WS1 + the WS2 worker API.
1. git clone https://github.com/sixstarstaffing/-margaux-content-director.git margaux && cd margaux
2. Read BUILD-SPRINT.md + deploy/API-CONTRACTS.md. RULE #1: no Mac files.
3. WS3: build the n8n trigger flow (Drive link in -> POST /jobs on the worker with the bearer secret) and the completion flow (worker callback -> update Supabase, Discord alert, hand approved items to WS6).
4. Acceptance: a submitted link creates a job row and the callback fires.
5. Report: python deploy/sprint/report.py --ws WS3 --status started --pct 0 --msg "n8n trigger flow" --push
```

## T5 · WS4 · Discord bot (wait for WS0 + WS2 API)
```
You are contractor terminal T5 (WS4, Discord bot) on the Margaux build sprint. Wait for WS0 secrets + WS2 API.
1. git clone https://github.com/sixstarstaffing/-margaux-content-director.git margaux && cd margaux
2. Read BUILD-SPRINT.md + deploy/API-CONTRACTS.md. RULE #1: no Mac files.
3. WS4: build the Discord bot: paste a Drive link -> triggers a job -> posts the routing sheet -> Iris-style tier approvals (tier1 auto / tier2 escalate to Kailin / tier3 reject) that flip approvals.state. Never auto-post.
4. Acceptance: paste link -> sheet posts -> approve flips approvals.state in Supabase.
5. Report: python deploy/sprint/report.py --ws WS4 --status started --pct 0 --msg "discord bot" --push
```

## T6 · WS5 · Netlify dashboard (wait for WS1)
```
You are contractor terminal T6 (WS5, Netlify dashboard) on the Margaux build sprint. Wait for WS1 schema.
1. git clone https://github.com/sixstarstaffing/-margaux-content-director.git margaux && cd margaux
2. Read BUILD-SPRINT.md + deploy/schema/001_init.sql. RULE #1: no Mac files. Forward-facing UI, no builder jargon.
3. WS5: build a Netlify page that reads Supabase with the ANON key (read-only) and renders the daily routing sheet + campaign tracker + shotlist per OUTPUT-TEMPLATE.md. Approvals write via the tight RLS policy only.
4. Acceptance: renders a real job's sheet/tracker/shotlist.
5. Report: python deploy/sprint/report.py --ws WS5 --status started --pct 0 --msg "dashboard scaffold" --push
```

## T7 · WS6 · BrandForge export (wait for WS1; needs BrandForge repo read)
```
You are contractor terminal T7 (WS6, BrandForge export) on the Margaux build sprint. Wait for WS1 schema.
1. git clone https://github.com/sixstarstaffing/-margaux-content-director.git margaux && cd margaux
2. ALSO clone the BrandForge repo READ-ONLY to match its formats (content-data.js / qa-items.json). Do NOT commit into BrandForge.
3. Read BUILD-SPRINT.md + MARGAUX-DEPLOY.md (BrandForge section). RULE #1: no Mac files.
4. WS6: build the export that renders APPROVED Margaux rows from Supabase into the content-data.js / qa-items.json shape the BrandForge portal already consumes, then the publish path to Blotato with publish-once (unique asset_id+platform).
5. Acceptance: an approved row appears in the (test) BrandForge portal and publishes once to a test destination.
6. Report: python deploy/sprint/report.py --ws WS6 --status started --pct 0 --msg "brandforge export" --push
```

## T8 · WS7 · Shared voice (wait for WS1)
```
You are contractor terminal T8 (WS7, shared voice) on the Margaux build sprint. Wait for WS1 schema.
1. git clone https://github.com/sixstarstaffing/-margaux-content-director.git margaux && cd margaux
2. Read BUILD-SPRINT.md + PERSONAL-BRAND.md + deploy/voice/plated-defaults-CONTEXT.md. RULE #1: no Mac files.
3. WS7: load the Plated voice (anchor, Voice v2.1 banned phrases, tiers, CURRENT facts July 30/Japan-cut) and Kailin's personal pillars+samples into the Supabase voice_profile table so GiGi and Margaux read one source. Do NOT copy the stale July 16/Japan facts.
4. Acceptance: both read voice_profile from the DB, not a file.
5. Report: python deploy/sprint/report.py --ws WS7 --status started --pct 0 --msg "voice into supabase" --push
```

## T9 · Command Center
```
You are terminal T9, the Command Center for the Margaux build sprint.
1. git clone https://github.com/sixstarstaffing/-margaux-content-director.git margaux && cd margaux
2. Read BUILD-SPRINT.md fully. You coordinate, you do not build workstreams.
3. Announce when WS0 secrets + WS1 schema are ready so WS2-WS7 can start. Guard RULE #1: if any terminal reports needing a Mac file, flag it as the POZD failure and stop it.
4. Run the rollup on a cadence and after each milestone: python deploy/sprint/rollup.py  (git-pulls all logs -> posts one consolidated status to Kailin's #build-updates). Keep logs/COMMAND-CENTER-LOG.md.
5. Surface blockers to Kailin immediately.
```

## T10 · Spare / Kailin
```
Overflow + review + approvals. Kailin watches #build-updates for contractor pings and the Command Center rollup, taps approvals, and answers escalated blockers. No clone needed unless taking over a lane.
```
