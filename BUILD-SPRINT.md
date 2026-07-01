# Margaux · PC Build Sprint · COMMAND CENTER

The single map for the multi-terminal build of Margaux (hosted content-director on Hostinger/n8n/Supabase/Netlify/Discord). Deploy plan scored 96/100. This is what each terminal reads first.

## RULE #1 · NO local-machine files (this killed POZD Sprint 3)
Every terminal works ONLY from a fresh `git clone` of the `margaux-content-director` repo + secrets pulled from the shared store. No terminal ever reads a path on Kailin's Mac (`~/.claude/...`, `~/Desktop/...`, a Drive desktop mount). If a task seems to need a Mac file, it is vendored in the repo (`deploy/voice/`, `deploy/playbook/`) or it is a bug, report it, do not reach across machines.

## Every terminal, step 1 (bootstrap)
Follow `deploy/sprint/TERMINAL-BOOTSTRAP.md`:
1. `git clone <repo-url> && cd margaux-content-director`
2. Read this file, then read your workstream row below.
3. Pull your test secrets from the shared store (never hardcode, never a Mac file).
4. Report in: `python deploy/sprint/report.py --ws WS<n> --status started --pct 0 --msg "on it"`

## Reporting (two-way Discord, wired)
- **Contractor terminal → Kailin AND Command Center:** every terminal runs `report.py` on start, on each milestone, on blocker, on done. It posts to the **#build-updates** channel (Kailin watches) AND relays to the **command-center** channel, and appends + pushes its own `logs/TERMINAL-WS<n>-LOG.md`.
- **Command Center → Kailin:** the command-center terminal runs `python deploy/sprint/rollup.py` (git pulls all logs, composes a consolidated status, posts to #build-updates). Run it on a cadence or after each contractor milestone.
- Kailin sees BOTH the raw contractor pings and the command-center rollup, in one channel.

## LAUNCH ORDER (open terminals in THIS order)
1. **Command Center FIRST** (terminal T9 below). It comes up before everything so it coordinates, captures logs, and announces readiness from minute one. Nothing else starts until it is watching.
2. Then **WS0 secrets + WS1 schema** (the sequential critical path).
3. Then **WS2-WS7 fan out**, but only once Command Center announces WS1 is frozen.

(The T-numbers below are just IDs, not launch order. Launch order is the 3 steps above.)

## Workstreams (10 terminals: 8 WS + Command Center + spare/Kailin)
Critical path is sequential: **Command Center up → WS0 secrets → WS1 schema** before the rest fan out. Do NOT start WS2/WS5/WS6/WS7 until WS1 is merged (the schema is a frozen contract).

| Terminal | WS | Owns | Depends on | Acceptance (real test) |
|---|---|---|---|---|
| T1 | **WS0** | Secrets: rotate LEAKED Blotato key, provision `.env` on Hermes, n8n creds, Supabase Vault, rclone OAuth, worker shared secret | Step 0 (repo pushed) | no secret in git; a fresh terminal gets test creds without a Mac file |
| T2 | **WS1** | Supabase `001_init.sql` + `002_rls.sql` + Storage bucket `margaux-frames` | WS0 | migration applies clean; frozen + versioned |
| T3 | WS2 | VPS worker: brain→Claude service, wire scripts, Linux deps, reconciler, cleanup, disk cap | WS0, WS1 | `triage-media.py --selftest` green on Hermes; one real E2E job |
| T4 | WS3 | n8n trigger + completion flows (per `deploy/API-CONTRACTS.md`) | WS1, WS2 API | link → job row → callback fires |
| T5 | WS4 | Discord bot + Iris-tier approvals | WS0, WS2 API | paste link → sheet posts → approve flips `approvals.state` |
| T6 | WS5 | Netlify dashboard (anon read from Supabase) | WS1 | renders a real job's sheet/tracker/shotlist |
| T7 | WS6 | BrandForge export (Supabase → `content-data.js`/`qa-items.json`) + publish-once | WS1 + BrandForge repo | approved row shows in portal, publishes once to a test dest |
| T8 | WS7 | Shared voice into `voice_profile` (GiGi + Margaux one source) | WS1 | both read the DB, not a file |
| T9 | **Command Center (OPEN THIS FIRST)** | Coordinate, run `rollup.py`, unblock, keep `logs/COMMAND-CENTER-LOG.md`, guard Rule #1, announce when WS1 is frozen | none, launches first | rollup posts to Kailin; no cross-machine file refs slip in |
| T10 | Spare / Kailin | Overflow, review, approvals | n/a | n/a |

Estimate: ~3 to 4 focused days. WS0+WS1 first (sequential), then 6 lanes in parallel.

## Definition of shipped (real test only, no Mac file touched)
From a fresh clone on the PC, real test Drive folder + test Supabase: paste link in Discord → job row → assets scored with verdicts → sheet to Discord + dashboard → approve one → appears in test BrandForge portal → publishes once. See MARGAUX-DEPLOY.md §E2E.

## Files
- Deploy architecture: `MARGAUX-DEPLOY.md`
- API + lifecycle: `deploy/API-CONTRACTS.md`
- Schema: `deploy/schema/001_init.sql`, `002_rls.sql`
- Secrets: `deploy/.env.template`
- Reporting: `deploy/sprint/report.py`, `deploy/sprint/rollup.py`
- Bootstrap: `deploy/sprint/TERMINAL-BOOTSTRAP.md`
- Logs: `logs/COMMAND-CENTER-LOG.md`, `logs/TERMINAL-WS<n>-LOG.md`
