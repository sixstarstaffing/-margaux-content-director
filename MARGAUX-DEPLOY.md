# Margaux · Hosted Deployment (BrandForge front-door agent)

Margaux is NOT a local-only skill in production. She runs as a hosted agent on Kailin's stack and feeds BrandForge. The `content-director` skill files remain the **brain spec / source of truth** for her judgment; the VPS executes that brain headlessly via the Claude API.

Stack: **Hostinger Hermes VPS · n8n · Supabase · Netlify · GitHub · Discord** (+ Blotato via BrandForge).

## Component map

| Layer | Runs on | Job |
|---|---|---|
| **Brain spec** | GitHub | The skill (SKILL.md + RUBRIC/ROUTING/HOOKS/BOARDS/TRENDS/FORMATS/PERSONAL-BRAND) is the ported system prompt + logic. Source of truth, Netlify + VPS deploy from here. |
| **Worker** | Hostinger Hermes VPS | rclone pull the Drive link → `triage-media.py` (ffmpeg, PySceneDetect, OpenCV best-frame, whisper) → call Claude API with the brain spec to score/route/hook → write results to Supabase. All heavy compute lives here, NOT on the Mac. |
| **Interface** | Discord bot (on Hermes) | Talk / approve / alert (CHAD/Iris pattern). Paste a Drive link, get the routing sheet, approve Iris-style tiers. Never auto-posts. |
| **Orchestration** | n8n | Trigger workflow (link in → kick the VPS worker) + completion workflow (worker done → write Supabase, Discord alert, hand approved items to GiGi/Studio). Mirrors GiGi's existing `gigi-chat-webhook.json`. |
| **Shared state** | Supabase | Margaux's manifest, scores, verdicts, routing decisions, approvals, campaign tracker, shotlist. THIS is the BrandForge integration: her approved picks land in the same DB the portal/Studio read. One DB = no drift. Also holds the shared voice profile GiGi + Margaux both read. |
| **Dashboard** | Netlify | Forward-facing daily routing sheet + campaign tracker + shotlist, rendered from Supabase (like the BrandForge portal). Kailin reviews/approves here or in Discord. Deploys from GitHub. |
| **Publish** | Blotato (existing BrandForge) | Approved items flow Margaux → Supabase → BrandForge portal → `publish.js` → Blotato → 9 platforms. Approval gate stays. |

## End-to-end flow
1. Kailin uploads footage to a Google Drive folder, drops the **link** in Discord (or a portal form).
2. **n8n** webhook fires → kicks the **VPS worker**.
3. Worker: `sync-drive.sh` mirrors the folder to VPS disk → `triage-media.py` extracts best frames + transcripts → **Claude API** (brain spec) scores, routes personal-first, writes hooks, tags series, runs the trend desk.
4. Worker writes assets + routing decisions to **Supabase**.
5. **n8n** completion: Discord posts the routing sheet, **Netlify** dashboard updates.
6. Kailin **approves** (Discord or dashboard). Approved = ready-to-fire, never auto-posted.
7. Approved items feed **BrandForge Studio / make-posts** → QA gate → **Blotato**.

## Supabase schema (sketch)
- `content_jobs` (id, drive_link, brand, status, created_at)
- `content_assets` (id, job_id, filename, type, best_frame_url, tech_score, content_score, brand_fit, verdict, reason)
- `routing_decisions` (asset_id, destination [plated|personal], platform, series, episode, hook_onscreen, hook_verbal, hook_visual, caption, cta, funnel_role, audio, timeliness, post_order)
- `approvals` (asset_id, tier, decision, decided_by, decided_at)
- `campaign_tracker` (brand, days_to_event, series_progress, cta_cadence, thin_spots)
- `shotlist` (job_id, gap, shot_to_capture)
- `voice_profile` (brand, section, body) or a pointer to the shared file, so GiGi + Margaux read one source.

## Build workstreams (this IS parallelizable across terminals)
Unlike the disk work, the deploy has independent lanes. The Supabase schema is the critical-path first step everyone builds on.

| WS | Work | Depends on | Rough |
|---|---|---|---|
| **WS1** | Supabase schema + migrations (the data contract) | none · DO FIRST | 1-2 hr |
| WS2 | VPS worker: port brain to a headless Claude-API service + wire the pipeline scripts + install ffmpeg/opencv/scenedetect/whisper/rclone on Hermes | WS1 | 3-5 hr |
| WS3 | n8n trigger + completion workflows | WS1, WS2 endpoint | 1-2 hr |
| WS4 | Discord bot (interface + Iris-style approvals) | WS2 | 2-3 hr |
| WS5 | Netlify dashboard (reads Supabase, forward-facing) | WS1 | 2-3 hr |
| WS6 | BrandForge integration (Margaux's Supabase output into portal/Studio/make-posts) | WS1 + existing BrandForge | 2 hr |
| WS7 | Shared voice wiring (Supabase/file, GiGi + Margaux one source) | WS1 | 1 hr |

Realistic: **~1 to 2 days** of focused build. WS1 then WS2 are the long poles; after WS1 the rest fan out across terminals. Follow `~/Desktop/AI-EMPLOYEE-PLAYBOOK/` (token minter, SOUL template, Iris gotchas).

## Notes
- The Mac's full disk no longer blocks Margaux, all compute is on Hermes. Mac cleanup + photo salvage is a separate track.
- whisper on the Linux VPS runs CPU-only (no Metal); use faster-whisper there, only on speech.
- The skill stays invocable locally for dev/testing; production is the hosted worker.
