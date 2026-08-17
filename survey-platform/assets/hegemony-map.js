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
    { key: 'gg', label: 'Greater Good', sub: 'The Good Truth', u:  1, will:  1, color: '#0d6b2f' },
    { key: 'le', label: 'Lesser Evil',  sub: 'The Bad Lie',    u: -1, will:  1, color: '#9c3a20' },
    { key: 'ge', label: 'Greater Evil', sub: 'The Bad Truth',  u: -1, will: -1, color: '#b81f1f' },
    { key: 'lg', label: 'Lesser Good',  sub: 'The Good Lie',   u:  1, will: -1, color: '#15708c' },
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

  // Distance from (u, will) to each of the four anchors. 0 on an anchor,
  // 2 to either side-neighbour, 2*sqrt(2) diagonally opposite, sqrt(2) to
  // all four from the origin.
  function distances(u, will) {
    const d = {};
    for (const a of ANCHORS) d['d_' + a.key] = Math.hypot(u - a.u, will - a.will);
    return d;
  }

  // The inverse, for redrawing a stored placement. Both opposing pairs give
  // the same answer, so summing and halving uses all four numbers.
  function fromDistances(d) {
    return {
      u:    (d.d_le ** 2 - d.d_gg ** 2 + d.d_ge ** 2 - d.d_lg ** 2) / 8,
      will: (d.d_lg ** 2 - d.d_gg ** 2 + d.d_ge ** 2 - d.d_le ** 2) / 8,
    };
  }

  function nearestAnchor(u, will) {
    let best = ANCHORS[0], bestD = Infinity;
    for (const a of ANCHORS) {
      const d = Math.hypot(u - a.u, will - a.will);
      if (d < bestD) { bestD = d; best = a; }
    }
    return best;
  }

  function quadrant(u, will) {
    if (u >  0 && will >  0) return 'Productive (Greater Good)';
    if (u <= 0 && will >  0) return 'Reductive (Lesser Evil)';
    if (u >  0 && will <= 0) return 'Constructive (Lesser Good)';
    return 'Regressive (Greater Evil)';
  }

  /* ---- rendering ---- */

  function el(name, attrs) {
    const node = document.createElementNS('http://www.w3.org/2000/svg', name);
    for (const [k, v] of Object.entries(attrs || {})) node.setAttribute(k, v);
    return node;
  }

  // How pronounced the taiji S is. With handles at +/-h the curve peaks at
  // 0.2887 * h, so 1.4 gives 0.404u. Full-length handles at +/-2u would peak
  // at 0.577u, which overshoots the reference artwork.
  const HANDLE = 1.4;

  function draw(opts) {
    const o = opts || {};
    const svg = el('svg', {
      class: 'hgm', viewBox: `0 0 ${S} ${S}`, role: 'application',
      'aria-label': o.label || 'Psochic Hegemony map. Drag each item onto the map to place it.',
    });

    // Good and Bad are not split down the middle: the boundary is a taiji S,
    // so Good reaches across the centre at the top and Bad reaches back under
    // it at the bottom. One cubic from (0u, +2will) to (0u, -2will), handles
    // pulled out along 0will -- Bad side first, Good second, which is the
    // order that puts Good on top. Swapping them mirrors the figure.
    const P = (u, will) => toPx(u, will).join(' ');
    const CURVE      = `C ${P(-HANDLE, 0)}, ${P(HANDLE, 0)}, ${P(0, -2)}`;
    const GOOD_FIELD = `M 0 0 L ${P(0, 2)} ${CURVE} L 0 ${S} Z`;
    const BAD_FIELD  = `M ${S} 0 L ${P(0, 2)} ${CURVE} L ${S} ${S} Z`;
    const SPLIT      = `M ${P(0, 2)} ${CURVE}`;

    // Both regions are built from the identical arc string, so they share an
    // exact boundary -- no mask registration to get wrong, no hairline seam.
    const uid  = 'hgm' + Math.random().toString(36).slice(2, 8);
    const defs = el('defs', {});
    const grad = (id, stops) => {
      const g = el('linearGradient',
        { id, gradientUnits: 'userSpaceOnUse', x1: 0, y1: 0, x2: 0, y2: S });
      for (const [offset, color, opacity] of stops)
        g.appendChild(el('stop', { offset, 'stop-color': color, 'stop-opacity': opacity }));
      defs.appendChild(g);
    };
    // One saturated hue per field, faded by opacity alone. Lightening the
    // colour toward white AND dropping opacity fades twice over, which leaves
    // the weak ends on bare paper however high the floor is set. Holding the
    // hue means 0.32 still reads as a clear light green or pink.
    grad(uid + 'good', [['0%', '#1faf52', 0.95], ['30%', '#1faf52', 0.78],
                        ['60%', '#22b355', 0.56], ['85%', '#26b95c', 0.40],
                        ['100%','#2cc063', 0.32]]);
    grad(uid + 'bad',  [['0%', '#d93b34', 0.32], ['15%', '#d93b34', 0.40],
                        ['40%', '#d63029', 0.56], ['70%', '#d62a23', 0.78],
                        ['100%','#d4231c', 0.95]]);
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

    // Halo behind every label -- they all sit over one gradient or the other.
    const halo = { stroke: '#ffffff', 'stroke-width': 2.6, 'paint-order': 'stroke' };
    const text = (attrs, s) => {
      const t = el('text', Object.assign({}, halo, attrs));
      t.textContent = s; svg.appendChild(t); return t;
    };

    text({ x: 8,      y: cy - 7, fill: '#46505e', 'font-size': 9, 'text-anchor': 'start',
           'letter-spacing': '.08em' }, 'GOOD  +u');
    text({ x: S - 8,  y: cy - 7, fill: '#46505e', 'font-size': 9, 'text-anchor': 'end',
           'letter-spacing': '.08em' }, '-u  BAD');
    text({ x: cx + 7, y: 13,     fill: '#46505e', 'font-size': 9, 'text-anchor': 'start',
           'letter-spacing': '.08em' }, 'ACTIVE  +will');
    text({ x: cx + 7, y: S - 6,  fill: '#46505e', 'font-size': 9, 'text-anchor': 'start',
           'letter-spacing': '.08em' }, '-will  SUPPRESSIVE');

    // Tick numbers, so a respondent has something to aim at.
    for (const n of [2, 1, -1, -2]) {
      const [tx] = toPx(n, 0), [, ty] = toPx(0, n);
      text({ x: tx, y: 10, fill: '#77808d', 'font-size': 7.5, 'text-anchor': 'middle',
             'stroke-width': 2 }, `${n}u`);
      text({ x: S - 4, y: ty + 2.6, fill: '#77808d', 'font-size': 7.5, 'text-anchor': 'end',
             'stroke-width': 2 }, `${n}w`);
    }

    for (const p of INNER) {
      const [px, py] = toPx(p.u, p.will);
      svg.appendChild(el('circle', { cx: px, cy: py, r: 5, fill: '#ffffff',
        'fill-opacity': 0.5, stroke: p.color, 'stroke-opacity': 0.8,
        'stroke-width': 1, 'stroke-dasharray': '2 2' }));
      text({ x: px, y: py + 15, fill: p.color, 'font-size': 7, 'text-anchor': 'middle',
             'stroke-width': 2 }, p.label);
    }

    svg.appendChild(el('circle', { cx, cy, r: 15, fill: '#ffffff',
      stroke: '#46505e', 'stroke-opacity': 0.6, 'stroke-width': 1.2 }));
    text({ x: cx, y: cy - 1, fill: '#16202b', 'font-size': 7.5,
           'text-anchor': 'middle', 'font-weight': 'bold', 'stroke-width': 2 }, 'No-one');
    text({ x: cx, y: cy + 8, fill: '#46505e', 'font-size': 6.5,
           'text-anchor': 'middle', 'stroke-width': 2 }, 'Confusion');

    for (const a of ANCHORS) {
      const [px, py] = toPx(a.u, a.will);
      svg.appendChild(el('circle', { cx: px, cy: py, r: 9, fill: a.color,
        'fill-opacity': 0.30, stroke: a.color, 'stroke-width': 1.8 }));
      text({ x: px, y: py - 15, fill: a.color, 'font-size': 9.5,
             'text-anchor': 'middle', 'font-weight': 'bold' }, a.label);
      text({ x: px, y: py + 21, fill: '#46505e', 'font-size': 7,
             'text-anchor': 'middle', 'stroke-width': 2.2 }, a.sub);
    }

    const layer = el('g', { class: 'tokens' });   // tokens sit above everything
    svg.appendChild(layer);
    return { svg, layer };
  }

  // Draw the placed tokens. `placed` is { tokenId: {u, will} }.
  function drawTokens(svg, layer, tokens, placed, opts) {
    const readonly = !!(opts && opts.readonly);
    layer.textContent = '';
    for (const tok of tokens) {
      const p = placed[tok.id];
      if (!p) continue;
      const [px, py] = toPx(p.u, p.will);
      const g = el('g', { class: 'tok' + (readonly ? ' ro' : ''), 'data-token': tok.id,
        tabindex: readonly ? '-1' : '0', role: 'button',
        'aria-label': `${tok.label}, ${quadrant(p.u, p.will)}${readonly ? '' : '. Drag to move.'}` });
      g.appendChild(el('circle', { cx: px, cy: py, r: 11, fill: 'transparent' }));
      g.appendChild(el('circle', { cx: px, cy: py, r: 6.5, fill: tok.color || '#16202b',
        stroke: '#ffffff', 'stroke-width': 2 }));

      // Label beside the dot, never above: the anchors own the space above
      // (their name) and below (their sub-title), so a centred label lands
      // straight on "Greater Good" whenever a token is placed near one.
      const flip = px > S - 110;
      const t = el('text', { x: px + (flip ? -13 : 13), y: py + 3.5,
        fill: '#16202b', 'font-size': 8.5, 'font-weight': 'bold',
        'text-anchor': flip ? 'end' : 'start' });
      t.textContent = tok.label;
      g.appendChild(t);
      layer.appendChild(g);

      // Backing plate, sized from the text once it has been laid out.
      const bb = t.getBBox();
      const plate = el('rect', { x: bb.x - 3, y: bb.y - 2,
        width: bb.width + 6, height: bb.height + 4, rx: 2,
        fill: '#ffffff', 'fill-opacity': 0.88,
        stroke: tok.color || '#16202b', 'stroke-opacity': 0.5, 'stroke-width': 0.7 });
      g.insertBefore(plate, t);
    }
  }

  // Screen -> viewBox via the SVG's own transform. Doing this with
  // getBoundingClientRect arithmetic is wrong by however much
  // preserveAspectRatio letterboxes the drawing inside a not-exactly-square
  // box -- enough to miss an anchor you clicked directly on.
  function pointFromEvent(svg, evt) {
    const pt = svg.createSVGPoint();
    pt.x = evt.clientX; pt.y = evt.clientY;
    const { x, y } = pt.matrixTransform(svg.getScreenCTM().inverse());
    const [u, will] = toUWill(x, y);
    return { u: clamp(u), will: clamp(will) };
  }

  global.Hegemony = {
    S, ANCHORS, INNER, HANDLE,
    toPx, toUWill, clamp,
    distances, fromDistances, nearestAnchor, quadrant,
    draw, drawTokens, pointFromEvent,
  };
})(window);
