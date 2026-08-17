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
--   survey_placements    one row per token dropped on a hegemony map.
--   survey_answers        one row per non-map answer.
--
-- Who can do what
--   Respondent   anonymous auth (Supabase Anonymous Sign-Ins). Writes and
--                re-reads its own response only -- same shape as the
--                original welfare survey's responses/answers tables.
--                There is no owner/admin role: nothing here needs a login.

create extension if not exists pgcrypto;

-- Supersedes two earlier cuts: the single-survey hs_* tables from the
-- first draft, and the surveys/owner-login registry from the second
-- (dropped because authoring moved local -- see builder.html).
drop table if exists hs_placements cascade;
drop table if exists hs_answers    cascade;
drop table if exists hs_responses  cascade;
drop table if exists surveys       cascade;
drop view  if exists v_hs_placements_classified;
drop view  if exists v_hs_step_summary;

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
-- The four distance columns are the stored truth: straight-line distance
-- from where the token was dropped to each canonical anchor, in the map's
-- own (u, will) units where the anchors sit at (+/-1, +/-1).
--
--   d_gg -> Greater Good  (+1u, +1will)   The Good Truth
--   d_le -> Lesser Evil   (-1u, +1will)   The Bad Lie
--   d_ge -> Greater Evil  (-1u, -1will)   The Bad Truth
--   d_lg -> Lesser Good   (+1u, -1will)   The Good Lie
--
-- 0 on the anchor itself, 2 to either side-neighbour, 2*sqrt(2) ~ 2.8284
-- diagonally opposite, sqrt(2) ~ 1.4142 to all four from the origin.
--
-- u and will are stored alongside. They are derivable from the four
-- distances (see the functions below), but they are what every query
-- actually filters and averages on.
-- ---------------------------------------------------------------------
create table if not exists survey_placements (
  response_id uuid not null references survey_responses(id) on delete cascade,
  step_id     text not null,
  token_id    text not null,
  d_gg numeric not null check (d_gg >= 0),
  d_le numeric not null check (d_le >= 0),
  d_ge numeric not null check (d_ge >= 0),
  d_lg numeric not null check (d_lg >= 0),
  u    numeric not null check (u    between -2 and 2),
  will numeric not null check (will between -2 and 2),
  map_variant text not null default 'outer',
  sequence    int,
  primary key (response_id, step_id, token_id, map_variant)
);

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
create or replace view v_placements_classified with (security_invoker = true) as
select
  p.*,
  r.survey_id,
  case
    when p.u >  0 and p.will >  0 then 'Productive (Greater Good)'
    when p.u <= 0 and p.will >  0 then 'Reductive (Lesser Evil)'
    when p.u >  0 and p.will <= 0 then 'Constructive (Lesser Good)'
    else                               'Regressive (Greater Evil)'
  end as quadrant,
  case least(p.d_gg, p.d_le, p.d_ge, p.d_lg)
    when p.d_gg then 'Greater Good'
    when p.d_le then 'Lesser Evil'
    when p.d_ge then 'Greater Evil'
    else             'Lesser Good'
  end as nearest_anchor,
  least(p.d_gg, p.d_le, p.d_ge, p.d_lg) as nearest_distance
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
--
-- NOTE: pgrst.db_pre_request is ONE setting for the whole project. If the
-- welfare survey's check_submission_rate is still registered, this replaces
-- it -- which is why this function throttles that table too rather than
-- just its own.
-- ---------------------------------------------------------------------
create schema if not exists private;

create table if not exists private.submission_log (
  ip         inet,
  request_at timestamp
);
create index if not exists idx_submission_log on private.submission_log (ip, request_at desc);

create or replace function public.check_submission_rate()
  returns void language plpgsql security definer set search_path = '' as $$
declare
  req_method text := current_setting('request.method', true);
  req_path   text := current_setting('request.path', true);
  req_ip     inet := split_part(
    current_setting('request.headers', true)::json->>'x-forwarded-for', ',', 1)::inet;
  recent_count   integer;
  max_per_window integer := 8;
  window_minutes integer := 60;
begin
  -- Only the insert that starts a new submission is counted; the placement
  -- and answer writes that follow ride in uncounted.
  if req_method is distinct from 'POST'
     or req_path not in ('survey_responses', 'responses') then
    return;
  end if;

  select count(*) into recent_count
  from private.submission_log
  where ip = req_ip and request_at > now() - (window_minutes || ' minutes')::interval;

  if recent_count >= max_per_window then
    raise sqlstate 'PGRST' using
      message = json_build_object(
        'message', 'Too many submissions from this address. Please try again later.')::text,
      detail  = json_build_object('status', 429, 'status_text', 'Too Many Requests')::text;
  end if;

  insert into private.submission_log (ip, request_at) values (req_ip, now());
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
