-- Margaux · RLS (WS1). SECURE DEFAULTS after the ship review flagged two holes in v1:
--   (1) anon could UPDATE approvals -> anyone with the public dashboard key could
--       flip an asset to 'approved' and push it to Blotato (broke never-auto-post).
--   (2) anon could SELECT every table -> public dashboard leaked drive_link + whisper
--       transcripts of Kailin's private video.
-- Fix: anon (the public key) gets NO access to base tables. Writes are service-role
-- (worker) only. Approvals require an AUTHENTICATED user. The dashboard reads a
-- sanitized, non-sensitive view.

alter table content_jobs        enable row level security;
alter table content_assets      enable row level security;
alter table routing_decisions   enable row level security;
alter table approvals           enable row level security;
alter table platform_posts      enable row level security;
alter table campaign_tracker    enable row level security;
alter table shotlist            enable row level security;
alter table voice_profile       enable row level security;

-- No anon policies on base tables = the public key can neither read nor write them.
-- drive_link, transcript, and all internals stay private; approvals can't be forged.

-- Dashboard read model: routing-sheet fields ONLY. No drive_link, no transcript,
-- no raw job internals. security_invoker so the caller's RLS still governs the base
-- tables (WS1: verify this does not leak; the SAFER option is to not expose Supabase
-- to the browser at all and have the dashboard fetch sanitized JSON from the worker).
create view public_sheet with (security_invoker = true) as
  select ca.id as asset_id, ca.job_id, ca.filename, ca.media_type,
         ca.best_frame_path, ca.verdict, ca.reason,
         rd.destination, rd.target_platform, rd.series, rd.episode,
         rd.hook_onscreen, rd.hook_verbal, rd.hook_visual, rd.caption, rd.cta,
         rd.role, rd.audio, rd.timeliness, rd.polish_notes, rd.post_order,
         ap.tier, ap.state as approval_state
  from content_assets ca
  left join routing_decisions rd on rd.asset_id = ca.id
  left join approvals ap on ap.asset_id = ca.id;

-- Approvals: an AUTHENTICATED user (Kailin signed in via Supabase Auth), never anon.
-- The dashboard must sign her in before approve/reject, OR route the tap through the
-- authenticated worker endpoint. No anon insert/update/delete anywhere.
create policy approvals_authed_decide on approvals
  for update to authenticated using (true) with check (state in ('approved','rejected'));
create policy sheet_read_authed on content_assets    for select to authenticated using (true);
create policy route_read_authed on routing_decisions  for select to authenticated using (true);

-- Everything else (inserts, publish rows, job writes) = service role (worker), which
-- bypasses RLS. No public path can create, approve, or publish.
