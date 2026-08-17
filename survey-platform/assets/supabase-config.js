/* Supabase connection, shared by the runner and the builder.

   The publishable key is meant to ship in the page -- it grants nothing on
   its own. schema.sql is what actually protects the data: RLS checks
   owner_id / respondent_id against auth.uid() on every row, and the
   pre-request throttle sits in front of the REST endpoint rather than
   behind this file's JS. */
window.SUPABASE_URL = 'https://iaudayzofxrgzwutittm.supabase.co';
window.SUPABASE_ANON_KEY = 'sb_publishable_WlfhOxEkAGDwAk5oZV2YrA_BIFfI0XN';

window.makeSupabase = function () {
  if (!window.supabase) return null;
  return window.supabase.createClient(window.SUPABASE_URL, window.SUPABASE_ANON_KEY);
};
