/* Driving logic for a self-contained exported survey page. Embedded whole
   into the exported HTML by builder.html's "Export survey HTML" -- this
   file is never loaded via <script src> itself, only its text content is
   copied inline, so it must not assume any other file exists alongside it.

   Two globals are set by a small inline <script> immediately before this
   one runs:
     window.__SURVEY_SLUG__   string, used as survey_id in Supabase writes
     window.__SURVEY_STEPS__  the steps array from the embedded definition  */
(function () {
'use strict';

const supa = window.makeSupabase ? window.makeSupabase() : null;
const B = window.SurveyBlocks;
const survey = { id: window.__SURVEY_SLUG__, slug: window.__SURVEY_SLUG__ };
const steps = window.__SURVEY_STEPS__ || [];

const view    = document.getElementById('view');
const progBar = document.getElementById('progBar');
const progNum = document.getElementById('progNum');

let state = B.blankState();
let stepIndex = 0;
let isComplete = () => true;
let responseId = null;
let submitted = false;

const storeKey = 'survey:' + survey.slug;

function restore() {
  try {
    const raw = localStorage.getItem(storeKey);
    if (!raw) return;
    const saved = JSON.parse(raw);
    state = Object.assign(B.blankState(), saved.state || {});
    responseId = saved.responseId || null;
    stepIndex = Math.min(saved.stepIndex || 0, Math.max(steps.length - 1, 0));
  } catch (e) { /* private mode or corrupt json -- start fresh */ }
}
function persist() {
  try { localStorage.setItem(storeKey, JSON.stringify({ state, responseId, stepIndex })); }
  catch (e) { /* storage blocked -- the run still works in memory */ }
}

function render() {
  view.textContent = '';
  const onLast = stepIndex >= steps.length;
  if (submitted) return renderDone();

  const eyebrow = document.createElement('p');
  eyebrow.className = 'eyebrow';
  eyebrow.textContent = onLast
    ? 'Review · ' + (steps.length + 1) + ' of ' + (steps.length + 1)
    : 'Step ' + (stepIndex + 1) + ' of ' + (steps.length + 1);
  view.appendChild(eyebrow);

  if (onLast) isComplete = renderReview();
  else isComplete = B.renderStep(steps[stepIndex], view, state, () => { persist(); updateNav(); });

  renderNav();
  updateNav();
  view.focus();
  window.scrollTo(0, 0);
}

function renderReview() {
  const h = document.createElement('h1'); h.textContent = 'Review and submit';
  const p = document.createElement('p'); p.className = 'prose';
  p.textContent = 'Optional: a name or alias and a rough area, so responses can be told apart and grouped. Neither is used to identify you.';
  view.append(h, p);

  const field = (key, label, ph) => {
    const l = document.createElement('label'); l.className = 'field'; l.textContent = label;
    const i = document.createElement('input');
    i.type = 'text'; i.placeholder = ph; i.value = state[key] || '';
    i.addEventListener('input', () => { state[key] = i.value; persist(); });
    view.append(l, i);
  };
  field('labelName', 'Name or alias', 'Optional');
  field('labelLocation', 'Suburb or region', 'Optional');

  const answered = steps.filter(s => s.type !== 'header').length;
  const placed = Object.values(state.placements).reduce((n, t) => n + Object.keys(t).length, 0);
  const sum = document.createElement('p');
  sum.className = 'msg'; sum.style.marginTop = '20px';
  sum.textContent = answered + ' questions · ' + placed + ' map placements.';
  view.appendChild(sum);
  return () => true;
}

function renderDone() {
  const h = document.createElement('h1'); h.textContent = 'Thank you';
  const p = document.createElement('p'); p.className = 'prose';
  p.textContent = 'Your response has been recorded. Below is what you said — yours only; nobody else’s answers are shown.';
  view.append(h, p);

  for (const step of steps) {
    if (step.type !== 'place') continue;
    if (!state.placements[step.id] || !Object.keys(state.placements[step.id]).length) continue;
    const wrap = document.createElement('div');
    wrap.style.margin = '34px 0 0';
    const t = document.createElement('h2'); t.textContent = step.heading;
    wrap.appendChild(t);
    view.appendChild(wrap);
    B.renderStep(Object.assign({}, step, { heading: null, body: null, image: null, followUp: null }),
                 view, state, () => {}, { readonly: true });
  }

  const again = document.createElement('div');
  again.className = 'nav';
  const edit = document.createElement('button');
  edit.className = 'btn ghost'; edit.textContent = 'Change my answers';
  edit.addEventListener('click', () => { submitted = false; stepIndex = 0; render(); });
  again.appendChild(edit);
  view.appendChild(again);

  progBar.style.width = '100%';
  progNum.textContent = 'done';
}

function renderNav() {
  const nav = document.createElement('div');
  nav.className = 'nav'; nav.id = 'nav';

  const back = document.createElement('button');
  back.className = 'btn ghost'; back.type = 'button'; back.textContent = 'Back';
  back.disabled = stepIndex === 0;
  back.addEventListener('click', () => { stepIndex--; persist(); render(); });
  nav.appendChild(back);

  const onLast = stepIndex >= steps.length;
  const next = document.createElement('button');
  next.className = 'btn'; next.id = 'nextBtn'; next.type = 'button';
  next.textContent = onLast ? 'Submit' : 'Continue';
  next.addEventListener('click', onLast ? submit : () => { stepIndex++; persist(); render(); });
  nav.appendChild(next);

  const msg = document.createElement('span');
  msg.className = 'msg'; msg.id = 'navMsg';
  nav.appendChild(msg);
  view.appendChild(nav);
}

function updateNav() {
  const btn = document.getElementById('nextBtn');
  if (btn) btn.disabled = !isComplete();
  progBar.style.width = (stepIndex / steps.length * 100) + '%';
  progNum.textContent = Math.min(stepIndex + 1, steps.length + 1) + '/' + (steps.length + 1);
}

// Anonymous sign-in gives a stable respondent id, so a second run from this
// browser updates the first row instead of creating a duplicate.
async function ensureSession() {
  if (!supa) return { error: { message: 'Supabase is not configured.' } };
  const { data: { session } } = await supa.auth.getSession();
  if (session) return { session };
  const { data, error } = await supa.auth.signInAnonymously();
  if (error) return { error };
  return { session: data.session };
}

async function submit() {
  const msg = document.getElementById('navMsg');
  const btn = document.getElementById('nextBtn');
  const set = (t, cls) => { msg.textContent = t; msg.className = 'msg' + (cls ? ' ' + cls : ''); };

  if (!supa) { set('Supabase is not configured — nothing was sent.', 'err'); return; }
  btn.disabled = true;
  set('Submitting…');

  const { session, error: authErr } = await ensureSession();
  if (authErr) { set(authErr.message, 'err'); btn.disabled = false; return; }

  const payload = B.buildExport(survey, state);
  const id = responseId || crypto.randomUUID();

  const { error: e1 } = await supa.from('survey_responses').upsert({
    id: id, survey_id: survey.slug, respondent_id: session.user.id,
    raw: payload, updated_at: new Date().toISOString(),
    label_name: payload.label.name, label_location: payload.label.location,
  }, { onConflict: 'id' });
  if (e1) { set(e1.message, 'err'); btn.disabled = false; return; }

  responseId = id;
  persist();

  const rows = B.toRows(id, state);
  for (const pair of [['survey_placements', rows.placements], ['survey_answers', rows.answers]]) {
    const table = pair[0], data = pair[1];
    const { error: delErr } = await supa.from(table).delete().eq('response_id', id);
    if (delErr) { set(table + ' cleanup: ' + delErr.message, 'err'); btn.disabled = false; return; }
    if (!data.length) continue;
    const { error } = await supa.from(table).insert(data);
    if (error) { set(table + ': ' + error.message, 'err'); btn.disabled = false; return; }
  }

  submitted = true;
  render();
}

if (!steps.length) {
  view.innerHTML = '';
  view.appendChild(Object.assign(document.createElement('p'),
    { className: 'msg err', textContent: 'This survey has no questions.' }));
} else {
  restore();
  render();
}
})();
