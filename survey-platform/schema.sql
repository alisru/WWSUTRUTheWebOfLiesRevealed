-- Survey platform -- Supabase schema.
-- Run once: Supabase dashboard -> SQL Editor -> paste -> Run. Safe to re-run.
--
-- Model
--   Authoring happens entirely offline, in builder.html: build a survey,
--   export a single self-contained HTML file, add it to the site yourself.
--   There is no live registry of surveys and nothing here needs updating
--   when a new survey is added -- these three tables just hold responses,
--   for any survey, forever.
--
--   survey_responses    one row per submitted run. `survey_id` is whatever
--                       slug the exported file embeds -- a plain string,
--                       not a foreign key, since there is no table of
--                       surveys to point at. `raw` is the whole payload.
--   survey_placements   one row per token dropped on a hegemony map.
--   survey_answers      one row per non-map answer.
--
-- Who can do what
--   Respondent   anonymous auth (Supabase Anonymous Sign-Ins). Writes and
--                re-reads its own response only -- same shape as the
--                original welfare survey's responses/answers tables.
--                There is no owner/admin role: nothing here needs a login.

create extension if not exists pgcrypto;

-- ---------------------------------------------------------------------
-- responses
-- ---------------------------------------------------------------------
create table if not exists survey_responses (
  id             uuid primary key default gen_random_uuid(),
  survey_id      text not null,        -- the slug embedded in the exported file
  respondent_id  uuid not null references auth.users(id) default auth.uid(),
  submitted_at   timestamptz not null default now(),
  updated_at     timestamptz not null default now(),
  label_name     text,
  label_location text,
  raw            jsonb not null
);

create index if not exists idx_survey_responses_survey     on survey_responses (survey_id);
create index if not exists idx_survey_responses_respondent on survey_responses (respondent_id);

-- One run per respondent per survey, so a second submission from the same
-- browser updates the first rather than adding a duplicate.
create unique index if not exists idx_survey_responses_one_per_respondent
  on survey_responses (survey_id, respondent_id);

-- ---------------------------------------------------------------------
-- placements
--
-- The distance columns are straight-line distance from where the token
-- was dropped to each anchor / preference point in (u, will) units:
--
--   Canonical Anchors:
--   d_gg -> Greater Good  (+1u, +1will)   The Good Truth
--   d_le -> Lesser Evil   (-1u, +1will)   The Bad Lie
--   d_ge -> Greater Evil  (-1u, -1will)   The Bad Truth
--   d_lg -> Lesser Good   (+1u, -1will)   The Good Lie
--
--   Preference Anchors:
--   d_gp -> Good Preference (+1u, 0will)  Productive Alignment
--   d_bp -> Bad Preference  (-1u, 0will)  Reductive Alignment
--
-- map_variant: 'perceptual' (with inner inversion ring) or 'non_inverted'
-- (clean map). map_variant is part of the primary key and v_step_summary
-- groups by it, so an undeclared value silently partitions the data --
-- hence the check constraint. The survey shipped 'outer' for a while; the
-- migration below folds those rows into 'perceptual', which is what that
-- map actually is.
-- ---------------------------------------------------------------------
create table if not exists survey_placements (
  response_id uuid not null references survey_responses(id) on delete cascade,
  step_id     text not null,
  token_id    text not null,
  d_gg numeric not null check (d_gg >= 0),
  d_le numeric not null check (d_le >= 0),
  d_ge numeric not null check (d_ge >= 0),
  d_lg numeric not null check (d_lg >= 0),
  d_gp numeric check (d_gp is null or d_gp >= 0),
  d_bp numeric check (d_bp is null or d_bp >= 0),
  u    numeric not null check (u    between -2 and 2),
  will numeric not null check (will between -2 and 2),
  placement_mode text not null default 'point',
  u_target    numeric check (u_target is null or (u_target between -2 and 2)),
  will_target numeric check (will_target is null or (will_target between -2 and 2)),
  magnitude   numeric check (magnitude is null or magnitude >= 0),
  vector_descriptor jsonb,
  map_variant text not null default 'perceptual',
  sequence    int,
  primary key (response_id, step_id, token_id, map_variant)
);

-- Fold any legacy 'outer' rows in before the constraint is applied. Safe to
-- re-run: after the first pass there is nothing left to update.
update survey_placements set map_variant = 'perceptual' where map_variant = 'outer';

do $$
begin
  if not exists (select 1 from pg_constraint where conname = 'survey_placements_map_variant_ck') then
    alter table survey_placements add constraint survey_placements_map_variant_ck
      check (map_variant in ('perceptual', 'non_inverted'));
  end if;
end $$;

create index if not exists idx_survey_placements_step on survey_placements (step_id, token_id);

-- ---------------------------------------------------------------------
-- non-map answers
-- ---------------------------------------------------------------------
create table if not exists survey_answers (
  response_id uuid not null references survey_responses(id) on delete cascade,
  step_id     text not null,
  choice      text[],        -- selected option labels
  other_text  text,          -- "other" write-in
  text_answer text,
  number_answer numeric,     -- scale blocks
  rank_order  text[],        -- ranking blocks, best first
  primary key (response_id, step_id)
);

-- ---------------------------------------------------------------------
-- Recover (u, will) from the four distances alone.
--   d_le^2 - d_gg^2 = 4u      d_ge^2 - d_lg^2 = 4u
--   d_lg^2 - d_gg^2 = 4will   d_ge^2 - d_le^2 = 4will
-- Both pairs agree, so summing and dividing by 8 uses all four.
-- ---------------------------------------------------------------------
create or replace function u_from_distances(d_gg numeric, d_le numeric, d_ge numeric, d_lg numeric)
  returns numeric language sql immutable set search_path = '' as $$
  select (d_le^2 - d_gg^2 + d_ge^2 - d_lg^2) / 8;
$$;

create or replace function will_from_distances(d_gg numeric, d_le numeric, d_ge numeric, d_lg numeric)
  returns numeric language sql immutable set search_path = '' as $$
  select (d_lg^2 - d_gg^2 + d_ge^2 - d_le^2) / 8;
$$;

-- ---------------------------------------------------------------------
-- Reviewer views. RLS on the base tables still applies through these --
-- security_invoker makes a view run as the querying user rather than its
-- owner, which is the Postgres default and would otherwise route around
-- the RLS policies below entirely.
-- ---------------------------------------------------------------------
-- Quadrant naming lives here and only here. The survey page has its own
-- quadrant() in JS for the live readout; if you change the strings, change
-- both -- they are user-facing labels and must agree.
create or replace function quadrant_of(u numeric, will numeric)
  returns text language sql immutable set search_path = '' as $$
  select case
    when u >  0 and will >  0 then 'Productive (Greater Good)'
    when u <= 0 and will >  0 then 'Reductive (Lesser Evil)'
    when u >  0 and will <= 0 then 'Constructive (Lesser Good)'
    else                           'Regressive (Greater Evil)'
  end;
$$;

-- Nearest reference point across everything survey_placements stores a
-- distance for. This used to consider only the four canonical anchors, so
-- the two preference points were invisible to analysis -- which mattered:
-- the survey has a whole topic (Everyday Preference) designed to land on
-- them, and every one of those responses got reported as whichever moral
-- corner happened to be least far away.
--
-- d_gp/d_bp are nullable (rows written before they were captured have no
-- value), so each is folded in only when present.
--
-- Confusion has no stored distance column -- it sits at the origin, so its
-- distance is just hypot(u, will) and is derived here. Leaving it out meant
-- a placement dead in the centre, the single most meaningful point on the
-- map, was reported as whichever preference anchor sorted first.
create or replace function nearest_point(
    u numeric, will numeric,
    d_gg numeric, d_le numeric, d_ge numeric, d_lg numeric,
    d_gp numeric default null, d_bp numeric default null)
  returns text language sql immutable set search_path = '' as $$
  select label from (values
    ('Greater Good',    d_gg), ('Lesser Evil',    d_le),
    ('Greater Evil',    d_ge), ('Lesser Good',    d_lg),
    ('Good Preference', d_gp), ('Bad Preference', d_bp),
    ('Confusion',       sqrt(u * u + will * will))
  ) as t(label, dist)
  where dist is not null
  order by dist, label
  limit 1;
$$;

-- Which marked inversion-ring point a placement is sitting on, if any.
-- The ring sits at half magnitude and is exactly sqrt(0.5) from three other
-- fixtures at once, so it can never win on nearest-distance alone -- it has
-- to be detected by proximity. RING_SNAP in the survey page is the same
-- 0.2 radius; keep the two in step.
create or replace function inversion_ring_point(u numeric, will numeric)
  returns text language sql immutable set search_path = '' as $$
  select label from (values
    ('Perc. Greater Evil',  0.5,  0.5), ('Perc. Lesser Good',  -0.5,  0.5),
    ('Perc. Lesser Evil',   0.5, -0.5), ('Perc. Greater Good', -0.5, -0.5)
  ) as t(label, rv, rpsi)
  where sqrt((u - rv) * (u - rv) + (will - rpsi) * (will - rpsi)) <= 0.2
  order by sqrt((u - rv) * (u - rv) + (will - rpsi) * (will - rpsi))
  limit 1;
$$;

create or replace view v_placements_classified with (security_invoker = true) as
select
  p.*,
  r.survey_id,
  quadrant_of(p.u, p.will) as quadrant,
  nearest_point(p.u, p.will, p.d_gg, p.d_le, p.d_ge, p.d_lg, p.d_gp, p.d_bp) as nearest_anchor,
  -- least() ignores nulls in Postgres, so the nullable preference columns
  -- need no coalescing -- rows written before they were captured simply
  -- fall back to the four canonical distances.
  least(p.d_gg, p.d_le, p.d_ge, p.d_lg, p.d_gp, p.d_bp,
        sqrt(p.u * p.u + p.will * p.will)) as nearest_distance,
  -- A placement on the ring is the respondent saying "this is where it is
  -- *perceived* to sit". Null for everything else, so `where
  -- perceived_point is not null` isolates exactly those responses.
  inversion_ring_point(p.u, p.will) as perceived_point
from survey_placements p
join survey_responses r on r.id = p.response_id;

-- Where a prompt lands on average, and how much respondents agree. A high
-- sd means the sample is split, not that the average respondent is
-- confused -- check it before reading the mean.
create or replace view v_step_summary with (security_invoker = true) as
select
  r.survey_id, p.step_id, p.token_id, p.map_variant,
  count(*)        as n,
  avg(p.u)        as avg_u,
  avg(p.will)     as avg_will,
  stddev_pop(p.u)    as sd_u,
  stddev_pop(p.will) as sd_will
from survey_placements p
join survey_responses r on r.id = p.response_id
group by r.survey_id, p.step_id, p.token_id, p.map_variant;

-- ---------------------------------------------------------------------
-- Row Level Security. Anonymous sign-ins use the `authenticated` role,
-- not `anon`, so every policy targets that. No table here grants anon
-- anything, and there is no owner/admin concept at all -- a respondent
-- can read and write their own response, full stop. Read your own
-- results by querying with your personal account against RLS, or with
-- the service-role key from the SQL Editor, which bypasses RLS entirely.
-- ---------------------------------------------------------------------
alter table survey_responses  enable row level security;
alter table survey_placements enable row level security;
alter table survey_answers    enable row level security;

grant select, insert, update, delete on table survey_responses  to authenticated;
grant select, insert, update, delete on table survey_placements to authenticated;
grant select, insert, update, delete on table survey_answers    to authenticated;

do $$
declare pol record;
begin
  for pol in
    select policyname, tablename from pg_policies
    where schemaname = 'public'
      and tablename in ('survey_responses','survey_placements','survey_answers')
  loop
    execute format('drop policy %I on %I', pol.policyname, pol.tablename);
  end loop;
end $$;

create policy "response own select" on survey_responses for select
  to authenticated using (respondent_id = (select auth.uid()));
create policy "response own insert" on survey_responses for insert
  to authenticated with check (respondent_id = (select auth.uid()));
create policy "response own update" on survey_responses for update
  to authenticated using (respondent_id = (select auth.uid()))
  with check (respondent_id = (select auth.uid()));
create policy "response own delete" on survey_responses for delete
  to authenticated using (respondent_id = (select auth.uid()));

-- Child tables inherit ownership through the parent response row.
do $$
declare t text;
begin
  foreach t in array array['survey_placements','survey_answers'] loop
    execute format($f$
      create policy %I on %I for select to authenticated
      using (exists (select 1 from survey_responses r
                     where r.id = %I.response_id
                       and r.respondent_id = (select auth.uid())))$f$,
      t||' own select', t, t);
    execute format($f$
      create policy %I on %I for insert to authenticated
      with check (exists (select 1 from survey_responses r
                          where r.id = %I.response_id
                            and r.respondent_id = (select auth.uid())))$f$,
      t||' own insert', t, t);
    execute format($f$
      create policy %I on %I for update to authenticated
      using (exists (select 1 from survey_responses r
                     where r.id = %I.response_id
                       and r.respondent_id = (select auth.uid())))$f$,
      t||' own update', t, t);
    execute format($f$
      create policy %I on %I for delete to authenticated
      using (exists (select 1 from survey_responses r
                     where r.id = %I.response_id
                       and r.respondent_id = (select auth.uid())))$f$,
      t||' own delete', t, t);
  end loop;
end $$;

-- ---------------------------------------------------------------------
-- updated_at
-- ---------------------------------------------------------------------
create or replace function touch_updated_at() returns trigger
  language plpgsql set search_path = '' as $$
begin new.updated_at := now(); return new; end;
$$;

drop trigger if exists responses_touch on survey_responses;
create trigger responses_touch before update on survey_responses
  for each row execute function touch_updated_at();

-- ---------------------------------------------------------------------
-- Row-spam throttle. Runs inside Supabase before every Data API request,
-- so it cannot be bypassed by calling the REST endpoint directly.
-- Pattern from Supabase's "Securing your API" guide.
-- ---------------------------------------------------------------------
create schema if not exists private;

create table if not exists private.submission_log (
  ip         inet,
  respondent uuid,
  request_at timestamptz
);
-- Older deployments created this table without `respondent`; add it in
-- rather than requiring a drop, so this file stays re-runnable.
alter table private.submission_log add column if not exists respondent uuid;

create index if not exists idx_submission_log on private.submission_log (ip, request_at desc);
create index if not exists idx_submission_log_respondent
  on private.submission_log (respondent, request_at desc);

create or replace function public.check_submission_rate()
  returns void language plpgsql security definer set search_path = '' as $$
declare
  req_method text := current_setting('request.method', true);
  req_path   text := current_setting('request.path', true);
  req_ip     inet;
  uid        uuid;
  per_ip     integer;
  per_user   integer;
  -- A survey link gets passed round an office, a classroom, or a share
  -- house, and every one of those respondents arrives on one NAT address.
  -- The old limit of 8/hour per IP locked out the ninth person in the room
  -- with no way through. Two limits instead: a generous per-IP ceiling that
  -- still stops a scripted flood, and a tight per-respondent one, since the
  -- thing actually worth throttling is one anonymous identity spamming rows
  -- and each submission from a legitimate respondent is an idempotent
  -- upsert of the same row anyway.
  max_per_ip     integer := 60;
  max_per_user   integer := 12;
  window_minutes integer := 60;
begin
  -- PostgREST reports request.path with a leading slash, and on some
  -- versions with the /rest/v1 mount point still attached. The previous
  -- exact-match list ('survey_responses', 'responses') therefore never
  -- matched anything, so this function returned early on every request and
  -- the throttle was silently inert. Match on the trailing segment.
  if req_method is distinct from 'POST'
     or split_part(trim(both '/' from coalesce(req_path, '')), '/', -1)
        not in ('survey_responses', 'responses') then
    return;
  end if;

  -- This function runs as a pre-request hook on EVERY Data API call, so a
  -- parse error here is not a failed throttle -- it is a 500 on the whole
  -- endpoint. Both settings are attacker-influenced or absent depending on
  -- deployment, so each is parsed defensively and simply drops out of the
  -- decision if it cannot be read.
  begin
    req_ip := split_part(
      current_setting('request.headers', true)::json->>'x-forwarded-for', ',', 1)::inet;
  exception when others then
    req_ip := null;
  end;

  begin
    uid := nullif(current_setting('request.jwt.claims', true)::json->>'sub', '')::uuid;
  exception when others then
    uid := null;
  end;

  if req_ip is not null then
    select count(*) into per_ip
    from private.submission_log
    where ip = req_ip and request_at > now() - make_interval(mins => window_minutes);

    if per_ip >= max_per_ip then
      raise sqlstate 'PGRST' using
        message = json_build_object(
          'message', 'Too many submissions from this network. Please try again later.')::text,
        detail  = json_build_object('status', 429, 'status_text', 'Too Many Requests')::text;
    end if;
  end if;

  if uid is not null then
    select count(*) into per_user
    from private.submission_log
    where respondent = uid and request_at > now() - make_interval(mins => window_minutes);

    if per_user >= max_per_user then
      raise sqlstate 'PGRST' using
        message = json_build_object(
          'message', 'You have resubmitted several times in the last hour. Please try again later.')::text,
        detail  = json_build_object('status', 429, 'status_text', 'Too Many Requests')::text;
    end if;
  end if;

  insert into private.submission_log (ip, respondent, request_at)
  values (req_ip, uid, now());
end;
$$;

alter role authenticator set pgrst.db_pre_request = 'public.check_submission_rate';
notify pgrst, 'reload config';

create or replace function private.trim_submission_log() returns trigger
  language plpgsql set search_path = '' as $$
begin
  delete from private.submission_log where request_at < now() - interval '2 hours';
  return new;
end;
$$;

drop trigger if exists trim_submission_log_trigger on private.submission_log;
create trigger trim_submission_log_trigger
  after insert on private.submission_log
  execute function private.trim_submission_log();
