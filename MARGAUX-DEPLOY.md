# Margaux · Hosted Deployment (BrandForge front-door agent)

Margaux runs HOSTED on Kailin's stack and feeds BrandForge. The `content-director` skill files are her **brain spec**; the VPS executes that brain headlessly via the Claude API. This plan is what the PC build sprint builds.

Stack: **Hostinger Hermes VPS · n8n · Supabase · Netlify · GitHub · Discord** (+ Blotato via BrandForge).

> Reworked after a no-mercy ship review scored the first draft 41/100. This version fixes: the missing repo, Mac-local dependencies, no secrets story, undefined API contracts, schema holes, Linux port, and the assumed BrandForge wire.

## RULE #1 · NO local-machine files (this killed POZD Sprint 3)
Every artifact a PC or VPS terminal needs lives in the **git repo, Supabase, Drive, or the VPS env**, never only on the Mac. The prior sprint broke because terminals called files that lived on the Mac while Kailin was on the PC. Guardrails now in place:
- The skill dir is now a **real git repo** (commit `4d1a4b3`). Push it to GitHub as `margaux-content-director`; every terminal `git clone`s it and has everything.
- The two Mac-local dependencies are **vendored into the repo**: `deploy/voice/plated-defaults-CONTEXT.md` and `deploy/playbook/` (PLAYBOOK.md, SOUL-template.md, token minter). No more `~/.claude/skills/plated-defaults/...` or `~/Desktop/AI-EMPLOYEE-PLAYBOOK/...` runtime refs.
- Secrets come from the VPS `.env` / n8n credential store / Supabase Vault (`deploy/.env.template`), never a Mac file, never hardcoded.
- No `~/Library/CloudStorage` Drive-desktop mount in production, Hermes uses rclone headless OAuth only.
- whisper model path is env-driven (`WHISPER_CPP_MODEL`), no `~/whisper.cpp` Mac defaults.
- Acceptance gate for every workstream: it must run from a fresh `git clone` on a machine that has never seen the Mac.

## Step 0 · make the source real (BEFORE any workstream)
1. `git clone` is impossible until it is on GitHub. `gh` is NOT installed on the Mac, so: install `gh` (or create the repo in the GitHub web UI) and `git remote add origin ... && git push -u origin main`. The local repo + first commit already exist.
2. Confirm the repo contains: brain spec (SKILL + all reference md), `scripts/`, `deploy/schema/001_init.sql`, `deploy/.env.template`, `deploy/API-CONTRACTS.md`, `deploy/voice/`, `deploy/playbook/`.
3. Name the **BrandForge repo/URL** in this plan (WS6 needs it): the `bf-deploy` / `SMMxNativeForge` project holding `make-posts.py`, `content-data.js`, `portal.html`, `publish.js`, `blotato.js`.

## Component map

| Layer | Runs on | Job |
|---|---|---|
| **Brain spec** | GitHub repo | Skill md files = the ported Claude system prompt + logic. Source of truth. |
| **Worker** | Hostinger Hermes VPS | rclone pull the Drive link → `triage-media.py` → Claude API (brain) scores/routes/hooks → writes Supabase → deletes pulled media. Absolute workdir `MARGAUX_WORKDIR`, concurrency + disk caps. |
| **Interface** | Discord bot (Hermes) | Paste a Drive link, get the routing sheet, approve Iris-style. Never auto-posts. |
| **Orchestration** | n8n | Trigger (link → `POST /jobs`) + completion callback (→ Supabase, Discord alert, hand approved to BrandForge). Holds the worker shared secret. |
| **Shared state** | Supabase | `deploy/schema/001_init.sql`. Jobs, assets, routing, approvals, publish results, campaign, shotlist, voice. The BrandForge integration point. Frames in Supabase Storage bucket `margaux-frames`. |
| **Dashboard** | Netlify | Forward-facing daily sheet + tracker + shotlist, anon read-only from Supabase. Deploys from GitHub. |
| **Publish** | Blotato via BrandForge | Approved rows → BrandForge publish path → Blotato → 9 platforms. Approval-gated, publish-once. |

## End-to-end flow
Drive link in Discord → n8n `POST /jobs` → VPS worker (sync → triage → Claude → Supabase, media cleaned up) → n8n callback → Discord sheet + Netlify dashboard → Kailin approves → approved rows exported to BrandForge → QA gate → Blotato → 9 platforms. Contracts + state machine: `deploy/API-CONTRACTS.md`.

## BrandForge integration (verified, not assumed)
The BrandForge portal today reads a generated `content-data.js` and `make-posts.py` emits `qa-items.json` + a localStorage "ready-to-fire" flag, it does NOT live-read Supabase. So WS6 does ONE of:
- (a) **Export step:** an n8n/worker job renders approved Margaux rows from Supabase into the `content-data.js` / `qa-items.json` shape the portal already consumes, OR
- (b) **Convert the portal** to read Margaux's Supabase directly.
Pick (a) for speed in the 30-day window (no portal rewrite). Either way, the wire is a named task, not an assumption.

## Linux pipeline notes (WS2 acceptance = `--selftest` passes on Hermes)
- Install on Hermes: `ffmpeg`, `python3-opencv`/`opencv-python`, `pillow-heif`, `scenedetect`, rclone.
- whisper: build `whisper.cpp` on Hermes and keep the existing binary path (script already checks `whisper-cli`/`whisper-cpp`/`main` + `WHISPER_CPP_MODEL`). If building is painful, add a `faster-whisper` branch to `triage-media.py` (the plan's fallback is now a real code task, not a hand-wave).
- `sync-drive.sh`: production uses ONLY the rclone path (folder-id). The Mac desktop-mount branch is dev-only.
- Best-frame scorer = the OpenCV proxy (no CLIP/torch needed).

## Supabase schema (frozen)
`deploy/schema/001_init.sql` is the frozen v1: enum states (no silent drops), FKs + indexes, idempotency keys, a `platform_posts` publish-result table, `voice_profile` for the shared voice, and asset-level brand (job-level `brand_context` is a hint only, fixing the job-vs-asset brand conflict). RLS policies land in `002_rls.sql` during WS1. **Do not start WS2/WS5/WS6/WS7 until WS1 is merged.**

## Build workstreams (parallel after the critical path)
| WS | Work | Depends on | Acceptance | Rough |
|---|---|---|---|---|
| **WS0** | Secrets: rotate the LEAKED Blotato key, provision `.env` on Hermes, n8n creds, Supabase Vault, rclone headless OAuth, worker shared secret | Step 0 | no secret in git; test creds reach a fresh terminal without Mac files | 2-3 hr |
| **WS1** | Supabase schema `001_init.sql` + `002_rls.sql`, Storage bucket | Step 0 | migration applies clean; frozen + versioned | 2-3 hr |
| WS2 | VPS worker: brain→Claude service + wire scripts + Linux deps + reconciler + cleanup | WS0, WS1 | `--selftest` green on Hermes; E2E job on a real test folder | 5-8 hr |
| WS3 | n8n trigger + completion flows | WS1, WS2 API | link → row → callback fires | 2-3 hr |
| WS4 | Discord bot + Iris-tier approvals | WS0, WS2 API | paste link → sheet posted → approve flips state | 3-4 hr |
| WS5 | Netlify dashboard (anon read) | WS1 | renders a real job's sheet/tracker/shotlist | 3-4 hr |
| WS6 | BrandForge export (Supabase → content-data.js/qa-items.json) + publish path | WS1 + BrandForge repo | approved row appears in portal, publishes once | 3-4 hr |
| WS7 | Shared voice into `voice_profile` (GiGi + Margaux one source) | WS1 | both read the DB, not a Mac file | 1-2 hr |

**Realistic: ~3 to 4 focused days** (the review was right that "1-2 days" was fantasy once secrets, contracts, the Linux port, and the BrandForge wire are real). WS0+WS1 are the sequential critical path; WS2-WS7 fan out across terminals after.

## E2E acceptance (definition of shipped, real test only)
From a fresh clone on the PC, with a real **test** Drive folder and a **test** Supabase: paste the link in Discord → job row appears → assets scored with verdicts → sheet posts to Discord + dashboard → approve one → it appears in the (test) BrandForge portal → publish-once to a test destination. No Mac file touched anywhere in the chain.

## Notes
- The Mac's full disk does NOT block Margaux, all compute is on Hermes. Mac cleanup + photo salvage is a separate track.
- Follow the vendored `deploy/playbook/` (token minter, SOUL template, Iris gotchas).
