/* The Psochic Hegemony map: geometry, the distance encoding, rendering, and
   drag-to-place. Shared by the runner (survey.html) and the builder preview,
   so both draw the same figure from the same numbers.

   Axes, matching CoreTools/hegemony_map.html:
     u    = Good <-> Bad          (+u is Good, and draws to the LEFT)
     will = Active <-> Suppressive (+will is Active, draws UP)
   The grid spans -2..2 on both; the four canonical anchors sit at +/-1.

   A placement is stored as four numbers: the distance from the dropped
   point to each anchor. See ../quad-encoding.md.                          */
(function (global) {
  'use strict';

  const S = 400;                                   // svg viewBox size

  // Straight out of canonicalAnchors in hegemony_map.html, with the colours
  // darkened for a white ground.
  const ANCHORS = [
    { key: 'gg', label: 'Greater Good', sub: 'Productive · The Good Truth', u:  1, will:  1, color: '#0d6b2f' },
    { key: 'le', label: 'Lesser Evil',  sub: 'Reductive · The Bad Lie',    u: -1, will:  1, color: '#9c3a20' },
    { key: 'ge', label: 'Greater Evil', sub: 'Regressive · The Bad Truth', u: -1, will: -1, color: '#b81f1f' },
    { key: 'lg', label: 'Lesser Good',  sub: 'Constructive · The Good Lie',   u:  1, will: -1, color: '#15708c' },
  ];

  // The 2 Preferences at +-1u, 0will.
  const PREFERENCES = [
    { key: 'gp', label: 'Good Preference', sub: 'Productive Alignment', u:  1, will:  0, color: '#1faf52' },
    { key: 'bp', label: 'Bad Preference',  sub: 'Reductive Alignment',  u: -1, will:  0, color: '#d93b34' },
  ];

  // The perceptual inversion ring. Standing where Greater Good *feels* right
  // puts you at (-0.5u, -0.5will), which is nearest Greater Evil -- the
  // inversion the calibration section is about.
  const INNER = [
    { label: 'Perc. Greater Evil', u:  0.5, will:  0.5, color: '#b81f1f' },
    { label: 'Perc. Lesser Good',  u: -0.5, will:  0.5, color: '#15708c' },
    { label: 'Perc. Lesser Evil',  u:  0.5, will: -0.5, color: '#9c3a20' },
    { label: 'Perc. Greater Good', u: -0.5, will: -0.5, color: '#0d6b2f' },
  ];

  const toPx    = (u, will) => [ (2 - u) * S / 4, (2 - will) * S / 4 ];
  const toUWill = (x, y)    => [ 2 - x * 4 / S, 2 - y * 4 / S ];
  const clamp   = n => Math.max(-2, Math.min(2, n));

  /* ---- the encoding ---- */

  function distances(u, will) {
    const d = {};
    for (const a of ANCHORS) d['d_' + a.key] = Math.hypot(u - a.u, will - a.will);
    for (const p of PREFERENCES) d['d_' + p.key] = Math.hypot(u - p.u, will - p.will);
    return d;
  }

  function fromDistances(d) {
    return {
      u:    (d.d_le ** 2 - d.d_gg ** 2 + d.d_ge ** 2 - d.d_lg ** 2) / 8,
      will: (d.d_lg ** 2 - d.d_gg ** 2 + d.d_ge ** 2 - d.d_le ** 2) / 8,
    };
  }

  function nearestAnchor(u, will) {
    const all = [...ANCHORS, ...PREFERENCES];
    let best = all[0], bestD = Infinity;
    for (const a of all) {
      const d = Math.hypot(u - a.u, will - a.will);
      if (d < bestD) { bestD = d; best = a; }
    }
    return best;
  }

  function quadrant(u, will) {
    if (u >  0 && will >  0) return 'Productive';
    if (u <= 0 && will >  0) return 'Reductive';
    if (u >  0 && will <= 0) return 'Constructive';
    return 'Regressive';
  }

  function quadrantFullName(u, will) {
    if (u >  0 && will >  0) return 'Productive (Greater Good)';
    if (u <= 0 && will >  0) return 'Reductive (Lesser Evil)';
    if (u >  0 && will <= 0) return 'Constructive (Lesser Good)';
    return 'Regressive (Greater Evil)';
  }

  // Vector analysis: [start quadrant, magnitude, linear end quadrant]
  function vectorAnalysis(u0, will0, u1, will1) {
    const startQuad = quadrant(u0, will0);
    const endQuad = quadrant(u1, will1);
    const du = u1 - u0;
    const dwill = will1 - will0;
    const mag = Math.hypot(du, dwill);
    return {
      startQuadrant: startQuad,
      endQuadrant: endQuad,
      magnitude: Number(mag.toFixed(3)),
      du: Number(du.toFixed(3)),
      dwill: Number(dwill.toFixed(3)),
      // [start quadrant, magnitude, linear end quadrant]
      descriptor: [startQuad, Number(mag.toFixed(2)), endQuad],
      label: `[${startQuad}, ${mag.toFixed(2)}, ${endQuad}]`
    };
  }

  /* ---- rendering ---- */

  function el(name, attrs) {
    const node = document.createElementNS('http://www.w3.org/2000/svg', name);
    for (const [k, v] of Object.entries(attrs || {})) node.setAttribute(k, v);
    return node;
  }

  const HANDLE = 1.4;

  function draw(opts) {
    const o = opts || {};
    const isNonInverted = (o.variant === 'non_inverted' || o.variant === 'outer' || o.hideInner === true || o.inversion === false || o.nonInverted === true);

    const svg = el('svg', {
      class: 'hgm', viewBox: `0 0 ${S} ${S}`, role: 'application',
      'aria-label': o.label || 'Psochic Hegemony map. Drag each item onto the map to place it.',
    });

    const P = (u, will) => toPx(u, will).join(' ');
    const CURVE      = `C ${P(-HANDLE, 0)}, ${P(HANDLE, 0)}, ${P(0, -2)}`;
    const GOOD_FIELD = `M 0 0 L ${P(0, 2)} ${CURVE} L 0 ${S} Z`;
    const BAD_FIELD  = `M ${S} 0 L ${P(0, 2)} ${CURVE} L ${S} ${S} Z`;
    const SPLIT      = `M ${P(0, 2)} ${CURVE}`;

    const uid  = 'hgm' + Math.random().toString(36).slice(2, 8);
    const defs = el('defs', {});
    const grad = (id, stops) => {
      const g = el('linearGradient',
        { id, gradientUnits: 'userSpaceOnUse', x1: 0, y1: 0, x2: 0, y2: S });
      for (const [offset, color, opacity] of stops)
        g.appendChild(el('stop', { offset, 'stop-color': color, 'stop-opacity': opacity }));
      defs.appendChild(g);
    };

    grad(uid + 'good', [['0%', '#1faf52', 0.95], ['30%', '#1faf52', 0.78],
                        ['60%', '#22b355', 0.56], ['85%', '#26b95c', 0.40],
                        ['100%','#2cc063', 0.32]]);
    grad(uid + 'bad',  [['0%', '#d93b34', 0.32], ['15%', '#d93b34', 0.40],
                        ['40%', '#d63029', 0.56], ['70%', '#d62a23', 0.78],
                        ['100%','#d4231c', 0.95]]);
    
    // Arrow marker definitions for vector answer mode
    const marker = el('marker', {
      id: uid + '-arrow', viewBox: '0 0 10 10', refX: '7', refY: '5',
      markerWidth: '6', markerHeight: '6', orient: 'auto-start-reverse'
    });
    marker.appendChild(el('path', { d: 'M 0 1.5 L 8 5 L 0 8.5 z', fill: '#16202b' }));
    defs.appendChild(marker);

    svg.appendChild(defs);

    svg.appendChild(el('rect', { x: 0, y: 0, width: S, height: S, fill: '#ffffff' }));
    svg.appendChild(el('path', { d: GOOD_FIELD, fill: `url(#${uid}good)` }));
    svg.appendChild(el('path', { d: BAD_FIELD,  fill: `url(#${uid}bad)`  }));
    svg.appendChild(el('path', { d: SPLIT, fill: 'none', stroke: '#6b7280',
      'stroke-opacity': 0.20, 'stroke-width': 11, 'stroke-linecap': 'round' }));
    svg.appendChild(el('path', { d: SPLIT, fill: 'none', stroke: '#4b5563',
      'stroke-opacity': 0.45, 'stroke-width': 1.2 }));

    for (let i = -2; i <= 2; i += 0.5) {
      const [gx] = toPx(i, 0), [, gy] = toPx(0, i);
      const major = Number.isInteger(i);
      svg.appendChild(el('line', { x1: gx, y1: 0, x2: gx, y2: S,
        stroke: '#16202b', 'stroke-opacity': major ? 0.16 : 0.07, 'stroke-width': 1 }));
      svg.appendChild(el('line', { x1: 0, y1: gy, x2: S, y2: gy,
        stroke: '#16202b', 'stroke-opacity': major ? 0.16 : 0.07, 'stroke-width': 1 }));
    }

    const [cx, cy] = toPx(0, 0);
    svg.appendChild(el('line', { x1: 0, y1: cy, x2: S, y2: cy,
      stroke: '#16202b', 'stroke-opacity': 0.42, 'stroke-width': 1.2 }));
    svg.appendChild(el('line', { x1: cx, y1: 0, x2: cx, y2: S,
      stroke: '#16202b', 'stroke-opacity': 0.42, 'stroke-width': 1.2 }));

    const halo = { stroke: '#ffffff', 'stroke-width': 2.6, 'paint-order': 'stroke' };
    const text = (attrs, s) => {
      const t = el('text', Object.assign({}, halo, attrs));
      t.textContent = s; svg.appendChild(t); return t;
    };

    if (!isNonInverted) {
      for (const p of INNER) {
        const [px, py] = toPx(p.u, p.will);
        svg.appendChild(el('circle', { cx: px, cy: py, r: 5, fill: '#ffffff',
          'fill-opacity': 0.5, stroke: p.color, 'stroke-opacity': 0.8,
          'stroke-width': 1, 'stroke-dasharray': '2 2' }));
        text({ x: px, y: py + 15, fill: p.color, 'font-size': 7, 'text-anchor': 'middle',
               'stroke-width': 2 }, p.label);
      }
    }

    svg.appendChild(el('circle', { cx, cy, r: 15, fill: '#ffffff',
      stroke: '#46505e', 'stroke-opacity': 0.6, 'stroke-width': 1.2 }));
    text({ x: cx, y: cy - 1, fill: '#16202b', 'font-size': 7.5,
           'text-anchor': 'middle', 'font-weight': 'bold', 'stroke-width': 2 }, 'No-one');
    text({ x: cx, y: cy + 8, fill: '#46505e', 'font-size': 6.5,
           'text-anchor': 'middle', 'stroke-width': 2 }, 'Confusion');

    for (const p of PREFERENCES) {
      const [px, py] = toPx(p.u, p.will);
      svg.appendChild(el('circle', { cx: px, cy: py, r: 7.5, fill: p.color,
        'fill-opacity': 0.28, stroke: p.color, 'stroke-width': 1.6 }));
      text({ x: px, y: py - 12, fill: p.color, 'font-size': 8.5,
             'text-anchor': 'middle', 'font-weight': 'bold', 'stroke-width': 2 }, p.label);
      text({ x: px, y: py + 18, fill: '#4b5563', 'fill-opacity': '0.65', 'font-size': 7,
             'text-anchor': 'middle', 'stroke-width': 2 }, `(${p.u > 0 ? '+'+p.u : p.u}υ, 0ψ)`);
    }

    for (const a of ANCHORS) {
      const [px, py] = toPx(a.u, a.will);
      svg.appendChild(el('circle', { cx: px, cy: py, r: 9, fill: a.color,
        'fill-opacity': 0.30, stroke: a.color, 'stroke-width': 1.8 }));
      text({ x: px, y: py - 15, fill: a.color, 'font-size': 9.5,
             'text-anchor': 'middle', 'font-weight': 'bold' }, a.label);
      text({ x: px, y: py + 21, fill: '#4b5563', 'fill-opacity': '0.65', 'font-size': 7,
             'text-anchor': 'middle', 'stroke-width': 2.2 }, a.sub);
    }

    // --- OVERLAY: Axis Labels, Corner Quadrants & Numeric Ticks (rendered directly along center axes) ---
    // Corner quadrant headers (faded ~50% as background guides)
    text({ x: 10,     y: 22,     fill: '#0d6b2f', opacity: '0.50', 'font-size': 9, 'text-anchor': 'start',
           'letter-spacing': '.10em', 'font-weight': 'bold' }, 'PRODUCTIVE');
    text({ x: S - 10, y: 22,     fill: '#9c3a20', opacity: '0.50', 'font-size': 9, 'text-anchor': 'end',
           'letter-spacing': '.10em', 'font-weight': 'bold' }, 'REDUCTIVE');
    text({ x: 10,     y: S - 12, fill: '#15708c', opacity: '0.50', 'font-size': 9, 'text-anchor': 'start',
           'letter-spacing': '.10em', 'font-weight': 'bold' }, 'CONSTRUCTIVE');
    text({ x: S - 10, y: S - 12, fill: '#b81f1f', opacity: '0.50', 'font-size': 9, 'text-anchor': 'end',
           'letter-spacing': '.10em', 'font-weight': 'bold' }, 'REGRESSIVE');

    // Central Horizontal (υ) Axis Labels (faded ~25%)
    text({ x: 8,      y: cy - 7, fill: '#374151', 'fill-opacity': '0.75', 'font-size': 9, 'font-weight': 'bold', 'text-anchor': 'start',
           'letter-spacing': '.08em' }, 'GOOD  +2υ');
    text({ x: S - 8,  y: cy - 7, fill: '#374151', 'fill-opacity': '0.75', 'font-size': 9, 'font-weight': 'bold', 'text-anchor': 'end',
           'letter-spacing': '.08em' }, '-2υ  BAD');

    // Central Vertical (ψ) Axis Labels & Ticks (faded 25%-40%)
    text({ x: cx + 7, y: 14,     fill: '#374151', 'fill-opacity': '0.75', 'font-size': 9, 'font-weight': 'bold', 'text-anchor': 'start',
           'letter-spacing': '.08em' }, 'ACTIVE  +2ψ');
    text({ x: cx + 7, y: S - 6,  fill: '#374151', 'fill-opacity': '0.75', 'font-size': 9, 'font-weight': 'bold', 'text-anchor': 'start',
           'letter-spacing': '.08em' }, '-2ψ  SUPPRESSIVE');
    text({ x: cx + 7, y: 103,    fill: '#4b5563', 'fill-opacity': '0.60', 'font-size': 8, 'font-weight': 'bold', 'text-anchor': 'start' }, '+1ψ');
    text({ x: cx + 7, y: 303,    fill: '#4b5563', 'fill-opacity': '0.60', 'font-size': 8, 'font-weight': 'bold', 'text-anchor': 'start' }, '-1ψ');

    const layer = el('g', { class: 'tokens' });
    svg.appendChild(layer);
    return { svg, layer, markerId: uid + '-arrow' };
  }

  // Draw placed tokens / vectors. Supports both point and vector placements.
  function drawTokens(svg, layer, tokens, placed, opts) {
    const readonly = !!(opts && opts.readonly);
    const markerId = opts && opts.markerId;
    layer.textContent = '';

    for (const tok of tokens) {
      const p = placed[tok.id];
      if (!p) continue;
      const col = tok.color || '#16202b';

      if (p.isVector || p.u_target != null) {
        // Vector mode rendering: arrow from (u, will) to (u_target, will_target)
        const [x0, y0] = toPx(p.u, p.will);
        const [x1, y1] = toPx(p.u_target != null ? p.u_target : p.u, p.will_target != null ? p.will_target : p.will);
        const g = el('g', { class: 'tok vector-tok' + (readonly ? ' ro' : ''), 'data-token': tok.id });

        const dx = x1 - x0, dy = y1 - y0;
        const len = Math.hypot(dx, dy);

        // Vector line shaft
        g.appendChild(el('line', {
          x1: x0, y1: y0, x2: x1, y2: y1,
          stroke: col, 'stroke-width': 3.5, 'stroke-linecap': 'round'
        }));

        // Prominent Arrowhead at (x1, y1)
        if (len > 3) {
          const angle = Math.atan2(dy, dx);
          const headLen = 12;
          const a1 = angle - Math.PI / 6;
          const a2 = angle + Math.PI / 6;
          const p1x = x1 - headLen * Math.cos(a1);
          const p1y = y1 - headLen * Math.sin(a1);
          const p2x = x1 - headLen * Math.cos(a2);
          const p2y = y1 - headLen * Math.sin(a2);
          g.appendChild(el('polygon', {
            points: `${x1},${y1} ${p1x},${p1y} ${p2x},${p2y}`,
            fill: col
          }));
        }

        // Origin point circle handle
        g.appendChild(el('circle', {
          cx: x0, cy: y0, r: 6.5, fill: col, stroke: '#ffffff', 'stroke-width': 2,
          class: 'vec-origin-handle', 'data-handle': 'origin', 'data-token': tok.id
        }));

        // Destination tip handle
        g.appendChild(el('circle', {
          cx: x1, cy: y1, r: 8, fill: '#ffffff', stroke: col, 'stroke-width': 2.5,
          class: 'vec-tip-handle', 'data-handle': 'tip', 'data-token': tok.id,
          'fill-opacity': 0.4
        }));

        // Vector label placed near midpoint
        const mx = (x0 + x1) / 2, my = (y0 + y1) / 2;
        const vInfo = vectorAnalysis(p.u, p.will, p.u_target != null ? p.u_target : p.u, p.will_target != null ? p.will_target : p.will);
        const labelText = `${tok.label}: ${vInfo.label}`;
        const t = el('text', {
          x: mx, y: my - 9, fill: '#16202b', 'font-size': 8.5, 'font-weight': 'bold',
          'text-anchor': 'middle'
        });
        t.textContent = labelText;
        g.appendChild(t);

        layer.appendChild(g);

        let bb;
        try { bb = t.getBBox(); } catch(e) {}
        if (!bb || !bb.width) {
          const estWidth = labelText.length * 5.2 + 8;
          bb = { x: mx - estWidth / 2, y: my - 17, width: estWidth, height: 12 };
        }

        const plate = el('rect', {
          x: bb.x - 3, y: bb.y - 2, width: bb.width + 6, height: bb.height + 4, rx: 2,
          fill: '#ffffff', 'fill-opacity': 0.92, stroke: col, 'stroke-opacity': 0.6, 'stroke-width': 0.8
        });
        g.insertBefore(plate, t);
      } else {
        // Standard Point mode rendering
        const [px, py] = toPx(p.u, p.will);
        const g = el('g', { class: 'tok' + (readonly ? ' ro' : ''), 'data-token': tok.id,
          tabindex: readonly ? '-1' : '0', role: 'button',
          'aria-label': `${tok.label}, ${quadrantFullName(p.u, p.will)}${readonly ? '' : '. Drag to move.'}` });
        g.appendChild(el('circle', { cx: px, cy: py, r: 11, fill: 'transparent' }));
        g.appendChild(el('circle', { cx: px, cy: py, r: 6.5, fill: col,
          stroke: '#ffffff', 'stroke-width': 2 }));

        const flip = px > S - 110;
        const t = el('text', { x: px + (flip ? -13 : 13), y: py + 3.5,
          fill: '#16202b', 'font-size': 8.5, 'font-weight': 'bold',
          'text-anchor': flip ? 'end' : 'start' });
        t.textContent = tok.label;
        g.appendChild(t);
        layer.appendChild(g);

        const bb = t.getBBox();
        const plate = el('rect', { x: bb.x - 3, y: bb.y - 2,
          width: bb.width + 6, height: bb.height + 4, rx: 2,
          fill: '#ffffff', 'fill-opacity': 0.88,
          stroke: col, 'stroke-opacity': 0.5, 'stroke-width': 0.7 });
        g.insertBefore(plate, t);
      }
    }
  }

  function pointFromEvent(svg, evt) {
    const pt = svg.createSVGPoint();
    pt.x = evt.clientX; pt.y = evt.clientY;
    const { x, y } = pt.matrixTransform(svg.getScreenCTM().inverse());
    const [u, will] = toUWill(x, y);
    return { u: clamp(u), will: clamp(will) };
  }

  global.Hegemony = {
    S, ANCHORS, PREFERENCES, INNER, HANDLE,
    toPx, toUWill, clamp,
    distances, fromDistances, nearestAnchor, quadrant, quadrantFullName, vectorAnalysis,
    draw, drawTokens, pointFromEvent,
  };
})(window);
