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
let savedStep = 0;
let isComplete = () => true;
let responseId = null;
let submitted = false;

const storeKey = 'survey:' + survey.slug;

let intro = {};
try {
  if (window.__SURVEY_INTRO__) {
    intro = typeof window.__SURVEY_INTRO__ === 'string' ? JSON.parse(window.__SURVEY_INTRO__) : window.__SURVEY_INTRO__;
  }
} catch (e) {}

function restore() {
  try {
    const raw = localStorage.getItem(storeKey);
    if (!raw) {
      stepIndex = (intro.enabled !== false) ? -1 : 0;
      return;
    }
    const saved = JSON.parse(raw);
    state = Object.assign(B.blankState(), saved.state || {});
    responseId = saved.responseId || null;
    savedStep = (saved.stepIndex != null && saved.stepIndex >= 0) ? saved.stepIndex : 0;
    // When intro is enabled, always land on Intro screen first so respondents see the welcome & resume button
    stepIndex = (intro.enabled !== false) ? -1 : savedStep;
  } catch (e) {
    stepIndex = (intro.enabled !== false) ? -1 : 0;
  }
}
function persist() {
  try { localStorage.setItem(storeKey, JSON.stringify({ state, responseId, stepIndex: Math.max(0, stepIndex) })); }
  catch (e) { /* storage blocked -- the run still works in memory */ }
}

function render() {
  view.textContent = '';
  if (submitted) return renderDone();
  if (stepIndex === -1 && intro.enabled !== false) return renderIntro();

  const onLast = stepIndex >= steps.length;
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

function renderIntro() {
  const eyebrow = document.createElement('p');
  eyebrow.className = 'eyebrow';
  eyebrow.textContent = intro.eyebrow || 'Research Survey';
  view.appendChild(eyebrow);

  const h = document.createElement('h1');
  h.textContent = intro.heading || (survey.title || 'Welcome');
  view.appendChild(h);

  const bodyLines = Array.isArray(intro.body) ? intro.body : (intro.body ? intro.body.split('\n') : []);
  if (bodyLines.length) {
    const prose = document.createElement('div');
    prose.className = 'prose';
    for (const line of bodyLines) {
      if (!line.trim()) continue;
      const p = document.createElement('p');
      p.textContent = line;
      prose.appendChild(p);
    }
    view.appendChild(prose);
  }

  if (intro.image) {
    const img = document.createElement('img');
    img.className = 'stepimg';
    img.src = intro.image;
    img.alt = '';
    view.appendChild(img);
  }

  const badges = document.createElement('div');
  badges.className = 'intro-badges';

  const estMins = intro.estimatedMinutes || Math.max(5, Math.ceil(steps.length * 1.2));
  const qCount = steps.filter(s => s.type !== 'header').length;
  const placeCount = steps.filter(s => s.type === 'place').length;

  const b1 = document.createElement('div');
  b1.className = 'intro-badge';
  b1.innerHTML = `⏱️ <strong>~${estMins} mins</strong>`;
  badges.appendChild(b1);

  const b2 = document.createElement('div');
  b2.className = 'intro-badge';
  b2.innerHTML = `📋 <strong>${qCount} questions</strong>${placeCount ? ` · ${placeCount} map${placeCount > 1 ? 's' : ''}` : ''}`;
  badges.appendChild(b2);

  const b3 = document.createElement('div');
  b3.className = 'intro-badge';
  b3.innerHTML = `🔒 <strong>Anonymous & Private</strong>`;
  badges.appendChild(b3);

  const b4 = document.createElement('div');
  b4.className = 'intro-badge';
  b4.innerHTML = `💾 <strong>JSON / PDF Export</strong>`;
  badges.appendChild(b4);

  view.appendChild(badges);

  const answeredSteps = Object.keys(state.choices).length + Object.keys(state.texts).length + Object.keys(state.numbers).length + Object.keys(state.ranks).length + Object.keys(state.placements).length;

  const ctaWrap = document.createElement('div');
  ctaWrap.className = 'nav';
  ctaWrap.style.marginTop = '28px';

  if (answeredSteps > 0) {
    const resumeBtn = document.createElement('button');
    resumeBtn.className = 'btn';
    resumeBtn.textContent = 'Resume Survey (Step ' + (savedStep + 1) + ' of ' + (steps.length + 1) + ') →';
    resumeBtn.addEventListener('click', () => {
      stepIndex = savedStep;
      persist();
      render();
    });
    ctaWrap.appendChild(resumeBtn);

    const restartBtn = document.createElement('button');
    restartBtn.className = 'btn ghost';
    restartBtn.textContent = 'Start Fresh';
    restartBtn.addEventListener('click', () => {
      state = B.blankState();
      stepIndex = 0;
      savedStep = 0;
      persist();
      render();
    });
    ctaWrap.appendChild(restartBtn);
  } else {
    const startBtn = document.createElement('button');
    startBtn.className = 'btn';
    startBtn.textContent = (intro.startButtonText || 'Start Survey') + ' →';
    startBtn.addEventListener('click', () => {
      stepIndex = 0;
      savedStep = 0;
      persist();
      render();
    });
    ctaWrap.appendChild(startBtn);
  }

  view.appendChild(ctaWrap);

  progBar.style.width = '0%';
  progNum.textContent = '0/' + (steps.length + 1);
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
  let ending = {};
  try {
    if (window.__SURVEY_ENDING__) {
      ending = typeof window.__SURVEY_ENDING__ === 'string' ? JSON.parse(window.__SURVEY_ENDING__) : window.__SURVEY_ENDING__;
    }
  } catch(e) {}

  const h = document.createElement('h1'); h.textContent = ending.title || 'Thank you';
  const p = document.createElement('p'); p.className = 'prose';
  p.textContent = ending.body || 'Your response has been recorded. Below is what you said — yours only; nobody else’s answers are shown.';
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

  if (ending.pushOnPreCompletion === false) {
    const saveOnlineBtn = document.createElement('button');
    saveOnlineBtn.className = 'btn';
    saveOnlineBtn.id = 'saveOnlineBtn';
    saveOnlineBtn.type = 'button';
    saveOnlineBtn.textContent = 'Save Response Online (Supabase)';
    const onlineStatus = document.createElement('span');
    onlineStatus.className = 'msg';
    onlineStatus.id = 'onlineSaveMsg';

    saveOnlineBtn.addEventListener('click', async () => {
      saveOnlineBtn.disabled = true;
      onlineStatus.className = 'msg';
      onlineStatus.textContent = 'Saving online…';

      if (!supa) {
        onlineStatus.className = 'msg err';
        onlineStatus.textContent = 'Supabase is not configured — unable to save online.';
        saveOnlineBtn.disabled = false;
        return;
      }

      const { session, error: authErr } = await ensureSession();
      if (authErr) {
        onlineStatus.className = 'msg err';
        onlineStatus.textContent = authErr.message;
        saveOnlineBtn.disabled = false;
        return;
      }

      const payload = B.buildExport(survey, state);
      const id = responseId || crypto.randomUUID();

      const { error: e1 } = await supa.from('survey_responses').upsert({
        id: id, survey_id: survey.slug, respondent_id: session.user.id,
        raw: payload, updated_at: new Date().toISOString(),
        label_name: payload.label.name, label_location: payload.label.location,
      }, { onConflict: 'id' });
      if (e1) {
        onlineStatus.className = 'msg err';
        onlineStatus.textContent = e1.message;
        saveOnlineBtn.disabled = false;
        return;
      }

      responseId = id;
      persist();

      const rows = B.toRows(id, state, survey);
      for (const pair of [['survey_placements', rows.placements], ['survey_answers', rows.answers]]) {
        const table = pair[0], data = pair[1];
        const { error: delErr } = await supa.from(table).delete().eq('response_id', id);
        if (delErr) {
          onlineStatus.className = 'msg err';
          onlineStatus.textContent = table + ' cleanup: ' + delErr.message;
          saveOnlineBtn.disabled = false;
          return;
        }
        if (!data.length) continue;
        const { error } = await supa.from(table).insert(data);
        if (error) {
          onlineStatus.className = 'msg err';
          onlineStatus.textContent = table + ': ' + error.message;
          saveOnlineBtn.disabled = false;
          return;
        }
      }

      onlineStatus.className = 'msg ok';
      onlineStatus.textContent = 'Saved online successfully ✓';
      saveOnlineBtn.textContent = 'Saved Online ✓';
    });

    again.append(saveOnlineBtn, onlineStatus);
  }

  if (ending.allowJson !== false) {
    const dlJson = document.createElement('button');
    dlJson.className = 'btn ghost';
    dlJson.type = 'button';
    dlJson.textContent = 'Download My Answers (JSON)';
    dlJson.addEventListener('click', () => {
      const payload = B.buildExport(survey, state);
      const filename = `response-${survey.slug || 'survey'}-${(responseId || 'export').slice(0, 8)}.json`;
      const blob = new Blob([JSON.stringify(payload, null, 2)], { type: 'application/json' });
      const a = document.createElement('a');
      a.href = URL.createObjectURL(blob);
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      a.remove();
    });
    again.appendChild(dlJson);
  }

  if (ending.allowPdf !== false) {
    const dlPdf = document.createElement('button');
    dlPdf.className = 'btn ghost';
    dlPdf.type = 'button';
    dlPdf.textContent = 'Download / Print PDF';
    dlPdf.addEventListener('click', () => {
      window.print();
    });
    again.appendChild(dlPdf);
  }

  const edit = document.createElement('button');
  edit.className = 'btn ghost'; edit.textContent = 'Change my answers';
  edit.addEventListener('click', () => { submitted = false; stepIndex = 0; render(); });
  again.appendChild(edit);
  view.appendChild(again);

  progBar.style.width = '100%';
  progNum.textContent = 'done';
}

function finishLocal() {
  submitted = true;
  persist();
  render();
}

function renderNav() {
  const nav = document.createElement('div');
  nav.className = 'nav'; nav.id = 'nav';

  const hasIntro = intro.enabled !== false;
  const back = document.createElement('button');
  back.className = 'btn ghost'; back.type = 'button'; back.textContent = 'Back';
  back.disabled = stepIndex === 0 && !hasIntro;
  back.addEventListener('click', () => {
    if (stepIndex === 0 && hasIntro) stepIndex = -1;
    else stepIndex--;
    persist(); render();
  });
  nav.appendChild(back);

  let ending = {};
  try {
    if (window.__SURVEY_ENDING__) {
      ending = typeof window.__SURVEY_ENDING__ === 'string' ? JSON.parse(window.__SURVEY_ENDING__) : window.__SURVEY_ENDING__;
    }
  } catch(e) {}

  const pushAuto = ending.pushOnPreCompletion !== false;
  const onLast = stepIndex >= steps.length;
  const next = document.createElement('button');
  next.className = 'btn'; next.id = 'nextBtn'; next.type = 'button';
  next.textContent = onLast ? (pushAuto ? 'Submit' : 'Finish Survey →') : 'Continue';
  next.addEventListener('click', onLast ? (pushAuto ? submit : finishLocal) : () => { stepIndex++; persist(); render(); });
  nav.appendChild(next);

  const msg = document.createElement('span');
  msg.className = 'msg'; msg.id = 'navMsg';
  nav.appendChild(msg);
  view.appendChild(nav);
}

function updateNav() {
  const btn = document.getElementById('nextBtn');
  if (btn) btn.disabled = !isComplete();
  const curStep = Math.max(0, stepIndex + 1);
  const totalSteps = steps.length + 1;
  progBar.style.width = (Math.max(0, stepIndex) / steps.length * 100) + '%';
  progNum.textContent = curStep + '/' + totalSteps;
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

function setupPrivacyModal() {
  const modal = document.getElementById('privacyModal');
  const openBtn = document.getElementById('openPrivacyBtn');
  const closeBtn = document.getElementById('closePrivacyBtn');
  if (!modal) return;
  if (openBtn) {
    openBtn.addEventListener('click', () => {
      if (typeof modal.showModal === 'function') modal.showModal();
      else modal.setAttribute('open', '');
    });
  }
  if (closeBtn) {
    closeBtn.addEventListener('click', () => {
      if (typeof modal.close === 'function') modal.close();
      else modal.removeAttribute('open');
    });
  }
  modal.addEventListener('click', e => {
    if (e.target === modal) {
      if (typeof modal.close === 'function') modal.close();
      else modal.removeAttribute('open');
    }
  });
}

setupPrivacyModal();

if (!steps.length) {
  view.innerHTML = '';
  view.appendChild(Object.assign(document.createElement('p'),
    { className: 'msg err', textContent: 'This survey has no questions.' }));
} else {
  restore();
  render();
}
})();
