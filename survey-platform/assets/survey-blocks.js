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
     placements { tokenId: { u, will, seq, isVector, u_target, will_target, du, dwill, magnitude, descriptor } } */
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
      blurb: 'Drag one or more items/vectors onto the map. Stores coordinates, distances, and trajectories.' },
  ];

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
                              mode: 'point', nonInverted: false, variant: 'perceptual',
                              tokens: [{ id: 'item', label: 'the item', color: '#3bde84' }] };
      default: throw new Error('unknown block type: ' + type);
    }
  }

  const blankState = () => ({ choices: {}, texts: {}, numbers: {}, ranks: {}, placements: {} });

  /* ------------------------------------------------------------------ *
   * Rendering
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
    if (!state.ranks[step.id]) state.ranks[step.id] = (step.items || []).slice();
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
    return () => true;
  }

  function renderPlace(step, host, state, onChange, opts) {
    const tokens = step.tokens || [];
    const variant = step.variant || (step.nonInverted ? 'non_inverted' : 'perceptual');
    const isVectorMode = (step.mode === 'vector' || step.placementMode === 'vector');

    if (!state.placements[step.id]) state.placements[step.id] = {};
    const placed = state.placements[step.id];
    const readonly = !!opts.readonly;

    const row = document.createElement('div');
    row.className = 'maprow';

    const mapbox = document.createElement('div');
    mapbox.className = 'mapbox';

    const size = Math.max(30, Math.min(100, (step.mapSize != null && Number(step.mapSize) > 0) ? Number(step.mapSize) : 100));
    if (size !== 100) {
      mapbox.style.width = size + '%';
      mapbox.style.margin = '0 auto';
    } else {
      mapbox.style.width = '100%';
    }

    const { svg, layer, markerId } = H.draw({ variant });
    mapbox.appendChild(svg);
    const tray = document.createElement('div');
    tray.className = 'tray';
    tray.innerHTML = `
      <div class="map-legend" style="background:var(--panel-2,#f6f8fa);border:1px solid var(--rule,#e5e7eb);border-radius:6px;padding:8px 10px;margin-bottom:12px;font-size:11px;line-height:1.4">
        <div style="font-weight:700;color:var(--ink,#111827);margin-bottom:5px;font-size:11.5px;letter-spacing:.02em">Map Coordinate Legend</div>
        <div style="margin-bottom:5px;color:var(--ink-soft,#4b5563)">
          <strong style="color:var(--ink,#111827)">&upsilon; (Morality / Benefit):</strong>
          <div style="font-size:10px;color:var(--ink-soft,#6b7280);margin-top:1px">
            <span style="color:#0d6b2f">+2</span> Everyone &middot; <span style="color:#15708c">+1</span> Others &middot; <span style="color:#46505e">0</span> Neutral &middot; <span style="color:#9c3a20">-1</span> My Group &middot; <span style="color:#b81f1f">-2</span> Only Me
          </div>
        </div>
        <div style="color:var(--ink-soft,#4b5563)">
          <strong style="color:var(--ink,#111827)">&psi; (Will):</strong>
          <div style="font-size:10px;color:var(--ink-soft,#6b7280);margin-top:1px">
            <span style="color:#0d6b2f">+2</span> Active &middot; <span style="color:#15708c">+1</span> Proactive &middot; <span style="color:#46505e">0</span> Neutral &middot; <span style="color:#9c3a20">-1</span> Passive &middot; <span style="color:#b81f1f">-2</span> Suppressive
          </div>
        </div>
      </div>
      <h3>${readonly ? 'Where you put them' : (isVectorMode ? 'Vectors to place' : 'Items to place')}</h3>`;
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
      }
      tray.appendChild(chip);
      chips.set(tok.id, chip);
    }

    if (!readonly) {
      const hint = document.createElement('div');
      hint.className = 'hint';
      if (isVectorMode) {
        hint.textContent = 'Click & drag on the map to set direction & magnitude from the starting point.';
      } else {
        hint.textContent = tokens.length > 1
          ? 'Drag each item onto the map, or select one and click where it belongs. Drag a placed dot to move it.'
          : 'Drag the item onto the map, or just click where it belongs.';
      }
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

    function placePoint(tokenId, u, will) {
      const existing = placed[tokenId];
      placed[tokenId] = { u, will, isVector: false, seq: existing ? existing.seq : Object.keys(placed).length + 1 };
      paint(); onChange();
    }

    function placeVector(tokenId, u0, will0, u1, will1) {
      const existing = placed[tokenId];
      const va = H.vectorAnalysis(u0, will0, u1, will1);
      placed[tokenId] = {
        u: u0, will: will0,
        u_target: u1, will_target: will1,
        isVector: true,
        du: va.du,
        dwill: va.dwill,
        magnitude: va.magnitude,
        descriptor: va.descriptor,
        trajectoryLabel: va.label,
        seq: existing ? existing.seq : Object.keys(placed).length + 1
      };
      paint(); onChange();
    }

    let activeDrag = null;

    if (!readonly) {
      svg.style.touchAction = 'none';

      svg.addEventListener('pointerdown', e => {
        const target = e.target;
        const handleType = target.dataset.handle;
        const targetTok = target.dataset.token;
        const pt = H.pointFromEvent(svg, e);

        if (isVectorMode) {
          e.preventDefault();
          try { svg.setPointerCapture(e.pointerId); } catch(err) {}

          if (handleType && targetTok && placed[targetTok]) {
            // Dragging an existing vector handle
            activeDrag = {
              mode: 'handle',
              handle: handleType,
              tokenId: targetTok,
              pointerId: e.pointerId,
              orig: Object.assign({}, placed[targetTok])
            };
          } else {
            // Dragging a new vector from point
            activeDrag = {
              mode: 'new_vector',
              tokenId: selected,
              pointerId: e.pointerId,
              u0: pt.u, will0: pt.will,
              u1: pt.u, will1: pt.will,
              moved: false
            };
            placeVector(selected, pt.u, pt.will, pt.u, pt.will);
          }
        } else {
          // Standard Point Click / Drag
          const { u, will } = H.pointFromEvent(svg, e);
          placePoint(selected, u, will);
          const next = tokens.find(t => !placed[t.id]);
          if (next) selected = next.id;
          paint();
        }
      });

      svg.addEventListener('pointermove', e => {
        if (!activeDrag || !isVectorMode) return;
        const pt = H.pointFromEvent(svg, e);

        if (activeDrag.mode === 'new_vector') {
          activeDrag.moved = true;
          activeDrag.u1 = pt.u;
          activeDrag.will1 = pt.will;
          placeVector(activeDrag.tokenId, activeDrag.u0, activeDrag.will0, pt.u, pt.will);
        } else if (activeDrag.mode === 'handle') {
          const cur = placed[activeDrag.tokenId];
          if (activeDrag.handle === 'origin') {
            const du = (cur.u_target != null ? cur.u_target : cur.u) - cur.u;
            const dwill = (cur.will_target != null ? cur.will_target : cur.will) - cur.will;
            placeVector(activeDrag.tokenId, pt.u, pt.will, H.clamp(pt.u + du), H.clamp(pt.will + dwill));
          } else if (activeDrag.handle === 'tip') {
            placeVector(activeDrag.tokenId, cur.u, cur.will, pt.u, pt.will);
          }
        }
      });

      const finishDrag = e => {
        if (!activeDrag || !isVectorMode) return;
        try { svg.releasePointerCapture(e.pointerId); } catch(err) {}

        if (activeDrag.mode === 'new_vector') {
          const cur = placed[activeDrag.tokenId];
          // If clicked without dragging, give a clear initial default arrow length (0.4w)
          if (!activeDrag.moved || Math.hypot(cur.u_target - cur.u, cur.will_target - cur.will) < 0.05) {
            const targetWill = cur.will >= 1.6 ? cur.will - 0.4 : cur.will + 0.4;
            placeVector(activeDrag.tokenId, cur.u, cur.will, cur.u, H.clamp(targetWill));
          }
          const next = tokens.find(t => !placed[t.id]);
          if (next) selected = next.id;
        }
        activeDrag = null;
        paint();
      };

      svg.addEventListener('pointerup', finishDrag);
      svg.addEventListener('pointercancel', finishDrag);
    }

    function paint() {
      H.drawTokens(svg, layer, tokens, placed, { readonly, markerId });

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

        if (p.isVector || isVectorMode) {
          const u1 = p.u_target != null ? p.u_target : p.u;
          const will1 = p.will_target != null ? p.will_target : p.will;
          const va = H.vectorAnalysis(p.u, p.will, u1, will1);
          rows.push(`
            <div style="margin-bottom:14px;background:var(--panel-2);padding:10px;border-radius:6px;border:1px solid var(--rule)">
              <div style="font-size:13px;font-weight:bold;margin-bottom:4px">${esc(tok.label)}</div>
              <div style="font-family:var(--mono);font-size:12px;color:var(--gg);margin-bottom:6px">
                Vector: [${esc(va.startQuadrant)}, ${va.magnitude.toFixed(2)}, ${esc(va.endQuadrant)}]
              </div>
              <div style="font-family:var(--mono);font-size:11px;color:var(--ink-soft);line-height:1.6">
                Start: (&upsilon; ${p.u.toFixed(2)}, &psi; ${p.will.toFixed(2)}) &middot; ${esc(va.startQuadrant)}<br>
                Target: (&upsilon; ${u1.toFixed(2)}, &psi; ${will1.toFixed(2)}) &middot; ${esc(va.endQuadrant)}<br>
                &Delta;&upsilon;: ${va.du >= 0 ? '+' : ''}${va.du.toFixed(2)} &middot; &Delta;&psi;: ${va.dwill >= 0 ? '+' : ''}${va.dwill.toFixed(2)} &middot; |v| = ${va.magnitude.toFixed(2)}
              </div>
            </div>`);
        } else {
          rows.push(`
            <div style="margin-bottom:12px">
              <div style="font-size:12px;color:var(--ink-soft);margin-bottom:5px">${esc(tok.label)}</div>
              <table class="rd">
                <tr><th></th><th>distance</th></tr>
                ${[...H.ANCHORS, ...(H.PREFERENCES||[])].map(a => `
                  <tr class="${a.key === near.key ? 'near' : ''}">
                    <td>${a.label}</td><td>${(d['d_' + a.key] != null ? d['d_' + a.key] : 0).toFixed(4)}</td>
                  </tr>`).join('')}
                <tr><td colspan="2" style="padding-top:6px;color:var(--ink-soft)">
                  (&upsilon; ${p.u.toFixed(2)}, &psi; ${p.will.toFixed(2)}) &nbsp; · &nbsp; ${H.quadrant(p.u, p.will)}
                </td></tr>
              </table>
            </div>`);
        }
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
   * Payload Export
   * ------------------------------------------------------------------ */
  function buildExport(survey, state) {
    const placements = {};
    for (const [stepId, toks] of Object.entries(state.placements)) {
      for (const [tokenId, p] of Object.entries(toks)) {
        const step = (survey.steps || []).find(s => s.id === stepId) || {};
        const isVec = !!(p.isVector || p.u_target != null);
        const u1 = isVec ? (p.u_target != null ? p.u_target : p.u) : p.u;
        const will1 = isVec ? (p.will_target != null ? p.will_target : p.will) : p.will;
        const va = isVec ? H.vectorAnalysis(p.u, p.will, u1, will1) : null;

        (placements[stepId] ||= {})[tokenId] = Object.assign(
          H.distances(p.u, p.will),
          {
            u: p.u, will: p.will,
            placement_mode: isVec ? 'vector' : 'point',
            u_target: isVec ? u1 : null,
            will_target: isVec ? will1 : null,
            magnitude: isVec ? va.magnitude : null,
            vector_descriptor: isVec ? va.descriptor : null,
            map_variant: step.variant || (step.nonInverted ? 'non_inverted' : 'perceptual'),
            nearest: H.nearestAnchor(p.u, p.will).label,
            quadrant: H.quadrant(p.u, p.will),
            sequence: p.seq
          });
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

  function toRows(responseId, state, survey) {
    const placements = [];
    const steps = (survey && survey.steps) || [];
    for (const [stepId, toks] of Object.entries(state.placements)) {
      const step = steps.find(s => s.id === stepId) || {};
      const mapVariant = step.variant || (step.nonInverted ? 'non_inverted' : 'perceptual');
      for (const [tokenId, p] of Object.entries(toks)) {
        const isVec = !!(p.isVector || p.u_target != null);
        const u1 = isVec ? (p.u_target != null ? p.u_target : p.u) : p.u;
        const will1 = isVec ? (p.will_target != null ? p.will_target : p.will) : p.will;
        const va = isVec ? H.vectorAnalysis(p.u, p.will, u1, will1) : null;

        placements.push(Object.assign(
          { response_id: responseId, step_id: stepId, token_id: tokenId },
          H.distances(p.u, p.will),
          {
            u: p.u, will: p.will,
            placement_mode: isVec ? 'vector' : 'point',
            u_target: isVec ? u1 : null,
            will_target: isVec ? will1 : null,
            magnitude: isVec ? va.magnitude : null,
            vector_descriptor: isVec ? JSON.stringify(va.descriptor) : null,
            map_variant: mapVariant,
            sequence: p.seq
          }));
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
