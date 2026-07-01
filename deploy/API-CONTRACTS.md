# Margaux · API contracts + job lifecycle (freeze before WS2/WS3/WS4 fan out)

So the worker, n8n, Discord bot, and dashboard terminals build to ONE agreed interface instead of guessing.

## Worker HTTP API (runs on Hermes)
Auth: `Authorization: Bearer $WORKER_SHARED_SECRET` on every call (n8n holds it in its credential store).

- `POST /jobs` → body `{ "drive_link": "...", "brand_context": "plated|personal|mixed" }`
  - resolves folder id, computes `content_hash`, UPSERTs `content_jobs` on `(drive_folder_id, content_hash)`.
  - returns `{ "job_id": "...", "status": "queued", "deduped": true|false }` (idempotent: same folder+content returns the existing job, does NOT re-run).
- `GET /jobs/{id}` → `{ status, counts, error }`.
- `POST /jobs/{id}/cancel` → best-effort stop + cleanup.
- Worker → n8n callback `POST $N8N_CALLBACK_URL` on terminal state: `{ job_id, status, summary }`.

## Job lifecycle (state machine, no silent drops)
```
queued → syncing → processing → scoring → done
   any state → failed (with error)   ↘ partial: a bad clip becomes an auto_rejected asset row, job continues
```
- **Heartbeat:** worker updates `content_jobs.heartbeat_at` every 30s while active.
- **Restart reconciler (WS2):** on boot, any job in syncing/processing/scoring with `heartbeat_at` older than 5 min → set `failed` (or requeue once) + Discord alert. No orphaned "running forever" rows.
- **Retry:** transient sync/API errors retry up to 3x with backoff; a per-asset ffmpeg failure does NOT fail the job, it writes an `auto_rejected` asset with reason and moves on.
- **Cleanup:** after the Supabase write, delete the pulled media from `MARGAUX_WORKDIR`; enforce `MARGAUX_DISK_BUDGET_GB` and `MARGAUX_MAX_CONCURRENT_JOBS`.

## Idempotency
- Job dedupe: unique `(drive_folder_id, content_hash)`; re-submitting the same link is a no-op that returns the existing job.
- Publish dedupe: unique `(asset_id, platform)` in `platform_posts`; publish-once even if approval fires twice.

## Approval → publish handoff (human-in-the-loop, never auto-post)
1. Worker writes `approvals` rows with a computed `tier`:
   - `tier1_auto` = personal Story/TikTok below the low bar can be greenlit fast (still surfaced, not published without a tap).
   - `tier2_escalate` = anything to a feed (Plated or personal) → needs Kailin.
   - `tier3_reject` = failed the gate → held with reason.
2. Kailin approves in Discord or the Netlify dashboard → sets `approvals.state='approved'`.
3. A Supabase trigger/n8n flow moves approved assets to the publish step, writing `platform_posts(status='queued')`.
4. The BrandForge publish path (see MARGAUX-DEPLOY §BrandForge) sends queued rows to Blotato, then writes back `published`/`failed` + `blotato_id`. Publish-once enforced by the unique constraint.
