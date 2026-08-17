/* Block types, rendering, and the answer payload. Shared by the runner and
   the builder preview, so what an author sees while editing is what a
   respondent gets.

   A survey definition is { steps: [ block, ... ] }. Every block has:
     id       stable string, unique within the survey. Answers key off this,
              so renaming one orphans its existing answers.
     type     one of BLOCK_TYPES below.
     heading  the question
     body     optional array of paragraphs shown under the heading
     image    optional URL
     required optional; ignored for `header`

   Answer state, all keyed by step id:
     choices    { selected: [label], other: '' }
     texts      string
     numbers    number
     ranks      [label]        best first
     placements { tokenId: { u, will, seq } }                              */
(function (global) {
  'use strict';

  const H = global.Hegemony;

  const BLOCK_TYPES = [
    { type: 'header', name: 'Section / text',
      blurb: 'Explanation with no input. Use for calibration copy and recaps.' },
    { type: 'choice', name: 'Multiple choice',
      blurb: 'Pick one, or several. Optional free-text "other".' },
    { type: 'text',   name: 'Free text',
      blurb: 'Short line or long-form answer.' },
    { type: 'scale',  name: 'Scale',
      blurb: 'A numeric run with labelled ends. Likert and similar.' },
    { type: 'rank',   name: 'Ranking',
      blurb: 'Put a list in order, best first.' },
    { type: 'place',  name: 'Hegemony placement',
      blurb: 'Drag one or more items onto the map. Stores four distances each.' },
  ];

  // A fresh block of each type, for the builder's "add" menu.
  function blankBlock(type, n) {
    const id = `${type}_${n}`;
    switch (type) {
      case 'header': return { id, type, heading: 'Section heading', body: [''] };
      case 'choice': return { id, type, heading: 'Your question?', required: true,
                              options: ['Option one', 'Option two'], multiple: false, allowOther: false };
      case 'text':   return { id, type, heading: 'Your question?', required: true, long: true };
      case 'scale':  return { id, type, heading: 'Your question?', required: true,
                              min: 1, max: 5, minLabel: 'Not at all', maxLabel: 'Completely' };
      case 'rank':   return { id, type, heading: 'Put these in order', required: true,
                              items: ['First thing', 'Second thing', 'Third thing'] };
      case 'place':  return { id, type, heading: 'Where would you place this?', required: true,
                              tokens: [{ id: 'item', label: 'the item', color: '#3bde84' }] };
      default: throw new Error('unknown block type: ' + type);
    }
  }

  const blankState = () => ({ choices: {}, texts: {}, numbers: {}, ranks: {}, placements: {} });

  /* ------------------------------------------------------------------ *
   * Rendering. Each renderer appends into `host` and returns a function
   * reporting whether the step is answered well enough to continue.
   * `onChange` is called after every edit so the caller can persist and
   * re-evaluate the Continue button.
   * ------------------------------------------------------------------ */
  function renderStep(step, host, state, onChange, opts) {
    const o = opts || {};

    if (step.heading) {
      const h = document.createElement('h1');
      h.textContent = step.heading;
      host.appendChild(h);
    }
    if (step.body && step.body.length) {
      const prose = document.createElement('div');
      prose.className = 'prose';
      for (const para of step.body) {
        if (!para) continue;
        const p = document.createElement('p');
        p.textContent = para;
        prose.appendChild(p);
      }
      if (prose.childNodes.length) host.appendChild(prose);
    }
    if (step.image) {
      const img = document.createElement('img');
      img.className = 'stepimg';
      img.src = step.image;
      img.alt = '';
      // A dead image URL should not leave a broken icon mid-survey.
      img.addEventListener('error', () => img.remove());
      host.appendChild(img);
    }

    switch (step.type) {
      case 'header': return () => true;
      case 'choice': return renderChoice(step, host, state, onChange);
      case 'text':   return renderText(step, host, state, onChange);
      case 'scale':  return renderScale(step, host, state, onChange);
      case 'rank':   return renderRank(step, host, state, onChange);
      case 'place':  return renderPlace(step, host, state, onChange, o);
      default: {
        const p = document.createElement('p');
        p.className = 'msg err';
        p.textContent = `Unknown block type "${step.type}" — skipped.`;
        host.appendChild(p);
        return () => true;
      }
    }
  }

  function renderChoice(step, host, state, onChange) {
    const cur = state.choices[step.id] || { selected: [], other: '' };
    state.choices[step.id] = cur;

    const box = document.createElement('div');
    box.className = 'opts';
    const multi = !!step.multiple;

    for (const opt of step.options || []) {
      const label = document.createElement('label');
      const input = document.createElement('input');
      input.type = multi ? 'checkbox' : 'radio';
      input.name = step.id;
      input.value = opt;
      input.checked = cur.selected.includes(opt);
      input.addEventListener('change', () => {
        cur.selected = [...box.querySelectorAll('input[type=radio]:checked,input[type=checkbox]:checked')]
          .map(i => i.value);
        onChange();
      });
      label.appendChild(input);
      label.appendChild(document.createTextNode(opt));
      box.appendChild(label);
    }

    if (step.allowOther) {
      const label = document.createElement('label');
      const input = document.createElement('input');
      input.type = multi ? 'checkbox' : 'radio';
      input.name = step.id;
      input.value = '__other__';
      input.checked = cur.selected.includes('__other__');
      label.appendChild(input);
      label.appendChild(document.createTextNode('Something else'));
      box.appendChild(label);

      const wrap = document.createElement('div');
      wrap.className = 'otherwrap';
      const txt = document.createElement('input');
      txt.type = 'text';
      txt.placeholder = 'Your answer';
      txt.value = cur.other || '';
      txt.addEventListener('input', () => { cur.other = txt.value; onChange(); });
      wrap.appendChild(txt);
      box.appendChild(wrap);

      input.addEventListener('change', () => {
        cur.selected = [...box.querySelectorAll('input[type=radio]:checked,input[type=checkbox]:checked')]
          .map(i => i.value);
        if (input.checked) txt.focus();
        onChange();
      });
    }

    host.appendChild(box);
    return () => {
      if (!step.required) return true;
      if (!cur.selected.length) return false;
      // Picking "Something else" without typing anything is not an answer.
      if (cur.selected.includes('__other__') && !(cur.other || '').trim()) return false;
      return true;
    };
  }

  function renderText(step, host, state, onChange) {
    const long = step.long !== false;
    const input = document.createElement(long ? 'textarea' : 'input');
    if (!long) input.type = 'text';
    if (step.placeholder) input.placeholder = step.placeholder;
    input.value = state.texts[step.id] || '';
    input.addEventListener('input', () => { state.texts[step.id] = input.value; onChange(); });
    host.appendChild(input);
    return () => !step.required || (state.texts[step.id] || '').trim().length > 0;
  }

  function renderScale(step, host, state, onChange) {
    const min = Number.isFinite(step.min) ? step.min : 1;
    const max = Number.isFinite(step.max) ? step.max : 5;

    const row = document.createElement('div');
    row.className = 'scalerow';
    for (let n = min; n <= max; n++) {
      const input = document.createElement('input');
      input.type = 'radio';
      input.name = step.id;
      input.id = `${step.id}_${n}`;
      input.value = String(n);
      input.checked = state.numbers[step.id] === n;
      input.addEventListener('change', () => { state.numbers[step.id] = n; onChange(); });
      const label = document.createElement('label');
      label.htmlFor = input.id;
      label.textContent = String(n);
      row.appendChild(input);
      row.appendChild(label);
    }
    host.appendChild(row);

    if (step.minLabel || step.maxLabel) {
      const ends = document.createElement('div');
      ends.className = 'scaleends';
      const a = document.createElement('span'); a.textContent = step.minLabel || '';
      const b = document.createElement('span'); b.textContent = step.maxLabel || '';
      ends.appendChild(a); ends.appendChild(b);
      host.appendChild(ends);
    }
    return () => !step.required || Number.isFinite(state.numbers[step.id]);
  }

  function renderRank(step, host, state, onChange) {
    // Seed from the definition on first view, then keep the respondent's order.
    if (!state.ranks[step.id]) state.ranks[step.id] = (step.items || []).slice();
    // If the author edited the items after someone started, drop and append
    // rather than showing stale entries.
    const items = state.ranks[step.id].filter(i => (step.items || []).includes(i));
    for (const i of step.items || []) if (!items.includes(i)) items.push(i);
    state.ranks[step.id] = items;

    const list = document.createElement('ol');
    list.className = 'ranklist';
    const paint = () => {
      list.textContent = '';
      state.ranks[step.id].forEach((item, idx) => {
        const li = document.createElement('li');
        const n = document.createElement('span');
        n.className = 'n'; n.textContent = String(idx + 1);
        const t = document.createElement('span');
        t.className = 't'; t.textContent = item;
        const up = document.createElement('button');
        up.type = 'button'; up.textContent = '↑';
        up.setAttribute('aria-label', `Move ${item} up`);
        up.disabled = idx === 0;
        up.addEventListener('click', () => { move(idx, idx - 1); });
        const dn = document.createElement('button');
        dn.type = 'button'; dn.textContent = '↓';
        dn.setAttribute('aria-label', `Move ${item} down`);
        dn.disabled = idx === state.ranks[step.id].length - 1;
        dn.addEventListener('click', () => { move(idx, idx + 1); });
        li.append(n, t, up, dn);
        list.appendChild(li);
      });
    };
    const move = (from, to) => {
      const arr = state.ranks[step.id];
      arr.splice(to, 0, arr.splice(from, 1)[0]);
      paint(); onChange();
    };
    paint();
    host.appendChild(list);
    return () => true;   // an order always exists
  }

  function renderPlace(step, host, state, onChange, opts) {
    const tokens = step.tokens || [];
    const variant = step.variant || 'outer';
    if (!state.placements[step.id]) state.placements[step.id] = {};
    const placed = state.placements[step.id];
    const readonly = !!opts.readonly;

    const row = document.createElement('div');
    row.className = 'maprow';
    const mapbox = document.createElement('div');
    mapbox.className = 'mapbox';
    const { svg, layer } = H.draw({});
    mapbox.appendChild(svg);
    const tray = document.createElement('div');
    tray.className = 'tray';
    tray.innerHTML = '<h3>' + (readonly ? 'Where you put them' : 'Items to place') + '</h3>';
    row.append(mapbox, tray);
    host.appendChild(row);

    let selected = (tokens.find(t => !placed[t.id]) || tokens[0] || {}).id;
    const chips = new Map();

    for (const tok of tokens) {
      const chip = document.createElement('div');
      chip.className = 'chip';
      chip.dataset.token = tok.id;
      const dot = document.createElement('span');
      dot.className = 'dot';
      dot.style.background = tok.color || '#3bde84';
      const name = document.createElement('span');
      name.textContent = tok.label;
      chip.append(dot, name);
      if (!readonly) {
        chip.tabIndex = 0;
        chip.addEventListener('click', () => { selected = tok.id; paint(); });
        chip.addEventListener('keydown', e => {
          if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); selected = tok.id; paint(); }
        });
        armDrag(chip, tok.id);
      }
      tray.appendChild(chip);
      chips.set(tok.id, chip);
    }

    if (!readonly) {
      const hint = document.createElement('div');
      hint.className = 'hint';
      hint.textContent = tokens.length > 1
        ? 'Drag each item onto the map, or select one and click where it belongs. Drag a placed dot to move it.'
        : 'Drag the item onto the map, or just click where it belongs.';
      tray.appendChild(hint);
    }

    const readout = document.createElement('div');
    readout.className = 'readout';
    tray.appendChild(readout);

    let clear = null;
    if (!readonly) {
      clear = document.createElement('button');
      clear.className = 'clr';
      clear.type = 'button';
      clear.textContent = 'Clear placements';
      clear.addEventListener('click', () => {
        state.placements[step.id] = {};
        Object.keys(placed).forEach(k => delete placed[k]);
        selected = (tokens[0] || {}).id;
        paint(); onChange();
      });
      tray.appendChild(clear);
    }

    function place(tokenId, u, will) {
      const existing = placed[tokenId];
      placed[tokenId] = { u, will, seq: existing ? existing.seq : Object.keys(placed).length + 1 };
      paint(); onChange();
    }

    let dragging = null, ghost = null;

    if (!readonly) {
      svg.addEventListener('click', e => {
        if (dragging) return;                 // pointerup already handled it
        const { u, will } = H.pointFromEvent(svg, e);
        place(selected, u, will);
        const next = tokens.find(t => !placed[t.id]);
        if (next) selected = next.id;
        paint();
      });
    }

    // One pointer-drag implementation, shared by tray chips and placed dots.
    function armDrag(node, tokenId) {
      node.addEventListener('pointerdown', e => {
        e.preventDefault();
        dragging = tokenId;
        selected = tokenId;
        const tok = tokens.find(t => t.id === tokenId) || {};
        ghost = document.createElement('div');
        ghost.className = 'dragghost';
        const d = document.createElement('span');
        d.style.cssText = `width:11px;height:11px;border-radius:50%;background:${tok.color || '#3bde84'}`;
        ghost.append(d, document.createTextNode(tok.label || ''));
        document.body.appendChild(ghost);
        moveGhost(e);

        const onMove = ev => moveGhost(ev);
        const onUp = ev => {
          document.removeEventListener('pointermove', onMove);
          document.removeEventListener('pointerup', onUp);
          if (ghost) { ghost.remove(); ghost = null; }
          const r = svg.getBoundingClientRect();
          if (ev.clientX >= r.left && ev.clientX <= r.right &&
              ev.clientY >= r.top  && ev.clientY <= r.bottom) {
            const { u, will } = H.pointFromEvent(svg, ev);
            place(tokenId, u, will);
          }
          // Deferred so the svg click handler can tell this was a drag.
          setTimeout(() => { dragging = null; }, 0);
          paint();
        };
        document.addEventListener('pointermove', onMove);
        document.addEventListener('pointerup', onUp);
      });
    }

    function moveGhost(e) {
      if (!ghost) return;
      ghost.style.left = e.clientX + 'px';
      ghost.style.top  = e.clientY + 'px';
    }

    function paint() {
      H.drawTokens(svg, layer, tokens, placed, { readonly });
      if (!readonly)
        for (const g of layer.querySelectorAll('.tok')) armDrag(g, g.dataset.token);

      for (const [id, chip] of chips) {
        chip.dataset.placed = !!placed[id];
        chip.classList.toggle('sel', !readonly && id === selected);
      }

      const rows = [];
      for (const tok of tokens) {
        const p = placed[tok.id];
        if (!p) continue;
        const d = H.distances(p.u, p.will);
        const near = H.nearestAnchor(p.u, p.will);
        rows.push(`
          <div style="margin-bottom:12px">
            <div style="font-size:12px;color:var(--ink-soft);margin-bottom:5px">${esc(tok.label)}</div>
            <table class="rd">
              <tr><th></th><th>distance</th></tr>
              ${H.ANCHORS.map(a => `
                <tr class="${a.key === near.key ? 'near' : ''}">
                  <td>${a.label}</td><td>${d['d_' + a.key].toFixed(4)}</td>
                </tr>`).join('')}
              <tr><td colspan="2" style="padding-top:6px;color:var(--ink-soft)">
                u ${p.u.toFixed(2)} &nbsp; will ${p.will.toFixed(2)} &nbsp; · &nbsp; ${H.quadrant(p.u, p.will)}
              </td></tr>
            </table>
          </div>`);
      }
      readout.innerHTML = rows.length ? rows.join('')
        : '<div style="font-size:12.5px;color:var(--ink-soft)">Nothing placed yet.</div>';
      if (clear) clear.style.display = rows.length ? '' : 'none';
    }

    paint();

    if (step.followUp && !readonly) {
      const lbl = document.createElement('p');
      lbl.style.cssText = 'margin:26px 0 8px;font-size:15px';
      lbl.textContent = step.followUp;
      host.appendChild(lbl);
      const ta = document.createElement('textarea');
      ta.value = state.texts[step.id] || '';
      ta.addEventListener('input', () => { state.texts[step.id] = ta.value; onChange(); });
      host.appendChild(ta);
    }

    return () => !step.required || tokens.every(t => placed[t.id]);
  }

  const esc = s => String(s).replace(/[&<>"]/g, c =>
    ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));

  /* ------------------------------------------------------------------ *
   * Payload
   * ------------------------------------------------------------------ */

  // The whole run, as stored in survey_responses.raw. Source of truth for
  // anything the normalized tables don't cover.
  function buildExport(survey, state) {
    const placements = {};
    for (const [stepId, toks] of Object.entries(state.placements)) {
      for (const [tokenId, p] of Object.entries(toks)) {
        (placements[stepId] ||= {})[tokenId] = Object.assign(
          H.distances(p.u, p.will),
          { u: p.u, will: p.will,
            nearest: H.nearestAnchor(p.u, p.will).label,
            quadrant: H.quadrant(p.u, p.will),
            sequence: p.seq });
      }
    }
    return {
      survey_id: survey.id, survey_slug: survey.slug, version: 1,
      completed_at: new Date().toISOString(),
      label: { name: state.labelName || null, location: state.labelLocation || null },
      choices: state.choices, texts: state.texts, numbers: state.numbers,
      ranks: state.ranks, placements,
    };
  }

  // Rows for the normalized tables, so aggregate queries are plain SQL.
  function toRows(responseId, state) {
    const placements = [];
    for (const [stepId, toks] of Object.entries(state.placements)) {
      for (const [tokenId, p] of Object.entries(toks)) {
        placements.push(Object.assign(
          { response_id: responseId, step_id: stepId, token_id: tokenId },
          H.distances(p.u, p.will),
          { u: p.u, will: p.will, map_variant: 'outer', sequence: p.seq }));
      }
    }

    const byStep = new Map();
    const row = id => {
      if (!byStep.has(id)) byStep.set(id, { response_id: responseId, step_id: id });
      return byStep.get(id);
    };
    for (const [id, c] of Object.entries(state.choices)) {
      if (!c || !c.selected || !c.selected.length) continue;
      const r = row(id);
      // Store the write-in under its own column rather than as the literal
      // sentinel, so `choice` only ever holds real option labels.
      r.choice = c.selected.map(s => (s === '__other__' ? 'Other' : s));
      if (c.selected.includes('__other__') && (c.other || '').trim()) r.other_text = c.other.trim();
    }
    for (const [id, t] of Object.entries(state.texts)) {
      if (!t || !t.trim()) continue;
      row(id).text_answer = t;
    }
    for (const [id, n] of Object.entries(state.numbers)) {
      if (!Number.isFinite(n)) continue;
      row(id).number_answer = n;
    }
    for (const [id, arr] of Object.entries(state.ranks)) {
      if (!arr || !arr.length) continue;
      row(id).rank_order = arr;
    }
    return { placements, answers: [...byStep.values()] };
  }

  global.SurveyBlocks = {
    BLOCK_TYPES, blankBlock, blankState, renderStep, buildExport, toRows,
  };
})(window);
