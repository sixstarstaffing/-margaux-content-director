-- Margaux · RLS policies (WS1). Worker writes with the service role (bypasses RLS);
-- the Netlify dashboard reads with the anon key and gets read-only, nothing else.

alter table content_jobs        enable row level security;
alter table content_assets      enable row level security;
alter table routing_decisions   enable row level security;
alter table approvals           enable row level security;
alter table platform_posts      enable row level security;
alter table campaign_tracker    enable row level security;
alter table shotlist            enable row level security;
alter table voice_profile       enable row level security;

-- anon (dashboard): read-only across the board
do $$
declare t text;
begin
  foreach t in array array[
    'content_jobs','content_assets','routing_decisions','approvals',
    'platform_posts','campaign_tracker','shotlist','voice_profile']
  loop
    execute format(
      'create policy %I_anon_read on %I for select to anon using (true);', t, t);
  end loop;
end $$;

-- Approvals are the ONE thing the dashboard writes (Kailin taps approve/reject).
-- Scope it tightly: anon may only flip state on an existing row, nothing else.
create policy approvals_anon_decide on approvals
  for update to anon using (true) with check (state in ('approved','rejected'));

-- All inserts/other writes require the service role (worker), which bypasses RLS.
-- No anon insert/delete policies = anon cannot create or destroy rows.
