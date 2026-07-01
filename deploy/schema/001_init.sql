-- Margaux · Supabase schema v1 (frozen artifact for the build sprint)
-- The shared brain + the BrandForge integration point. Every terminal builds
-- against THIS file. Do not fan out downstream workstreams until this is merged.

-- ---------- enums (explicit state, no silent drops) ----------
create type job_status      as enum ('queued','syncing','processing','scoring','done','failed');
create type asset_verdict   as enum ('assessed','deduped','auto_rejected','ready','polish','held','killed');
create type destination     as enum ('plated','personal');
create type platform        as enum ('ig_feed','ig_story','tiktok','reels');
create type funnel_role      as enum ('awareness','build','soft_cta','hard_cta');
create type timeliness       as enum ('evergreen','within_7d','within_48h');
create type approval_tier    as enum ('tier1_auto','tier2_escalate','tier3_reject');
create type approval_state   as enum ('pending','approved','rejected');
create type publish_status   as enum ('queued','published','failed');

-- ---------- jobs ----------
create table content_jobs (
  id            uuid primary key default gen_random_uuid(),
  drive_link    text not null,
  drive_folder_id text not null,
  content_hash  text,                       -- idempotency: hash of folder listing
  brand_context text,                       -- HINT only; real brand is per-asset (routing_decisions)
  status        job_status not null default 'queued',
  uploaded_count int, assessed_count int, deduped_count int, rejected_count int,
  error         text,
  heartbeat_at  timestamptz,                -- restart reconciler watches this
  created_at    timestamptz not null default now(),
  updated_at    timestamptz not null default now(),
  unique (drive_folder_id, content_hash)    -- same folder+content = one job (idempotent)
);

-- ---------- assets (one row per photo/clip, always a verdict) ----------
create table content_assets (
  id            uuid primary key default gen_random_uuid(),
  job_id        uuid not null references content_jobs(id) on delete cascade,
  filename      text not null,
  media_type    text not null,              -- photo | video
  duration_s    numeric,
  best_frame_path text,                     -- Supabase Storage object key (bucket: margaux-frames)
  tech_score    int, content_score int,
  brand_fit     text,                       -- plated_specific | either | personal_specific | off_brand
  verdict       asset_verdict not null default 'assessed',
  reason        text not null,              -- required: nothing exits without a written reason
  transcript    text,
  scored_on_visuals_only boolean default false,
  created_at    timestamptz not null default now()
);
create index on content_assets(job_id);
create index on content_assets(verdict);

-- ---------- routing (per asset: where/how it posts) ----------
create table routing_decisions (
  asset_id      uuid primary key references content_assets(id) on delete cascade,
  destination   destination not null,
  target_platform platform not null,
  series        text, episode text,
  hook_onscreen text, hook_verbal text, hook_visual text,
  caption       text,
  cta           text,
  role          funnel_role not null,
  audio         text,                       -- candidate sound, verify in-app
  timeliness    timeliness not null default 'evergreen',
  polish_notes  text,
  post_order    int
);

-- ---------- approvals (Iris-style tiers, human-in-the-loop) ----------
create table approvals (
  id            uuid primary key default gen_random_uuid(),
  asset_id      uuid not null references content_assets(id) on delete cascade,
  tier          approval_tier not null,
  state         approval_state not null default 'pending',
  decided_by    text, decided_at timestamptz,
  unique (asset_id)
);

-- ---------- publish results (Blotato handoff, publish-once) ----------
create table platform_posts (
  id            uuid primary key default gen_random_uuid(),
  asset_id      uuid not null references content_assets(id) on delete cascade,
  platform      platform not null,
  blotato_id    text,
  status        publish_status not null default 'queued',
  published_at  timestamptz, error text,
  unique (asset_id, platform)               -- one post per asset per platform (idempotent publish)
);

-- ---------- campaign tracker (30-day arc) ----------
create table campaign_tracker (
  id            uuid primary key default gen_random_uuid(),
  brand         text not null,
  snapshot_date date not null,
  days_to_event int,
  series_progress jsonb, cta_cadence jsonb, thin_spots text,
  unique (brand, snapshot_date)
);

-- ---------- shotlist (coverage -> next shoot) ----------
create table shotlist (
  id            uuid primary key default gen_random_uuid(),
  job_id        uuid references content_jobs(id) on delete cascade,
  gap           text not null, shot_to_capture text not null
);

-- ---------- shared voice (machine-independent; GiGi + Margaux read here) ----------
create table voice_profile (
  brand         text not null,
  section       text not null,              -- anchor | banned_phrases | pillars | samples | facts
  body          text not null,
  updated_at    timestamptz not null default now(),
  primary key (brand, section)
);

-- RLS: service role writes (worker), anon read-only for the Netlify dashboard.
-- (policies added in 002_rls.sql during WS1)
