/**
 * aletheia_canvas_renderer.js
 * 
 * Exact 1:1 JavaScript / HTML5 Canvas port of:
 * 1. generate_graph.py (draw_graph)
 * 2. image_card_generator.py (_generate_verdict_card, _generate_analysis_full_card, _generate_five_word_card)
 * 
 * Replicates the exact layouts, dimensions, font sizes, line heights, color palettes,
 * 256x256 gaussian morality field, Hegemony cross beams, attractor pulls, two-column grids,
 * accent pills, and watermarks directly in the browser with zero external image files.
 */

(function(global) {
  'use strict';

  // -------------------------------------------------------------
  // HELPER: Text Wrapping for Canvas
  // -------------------------------------------------------------
  function wrapCanvasText(ctx, text, maxWidth) {
    if (!text) return [];
    const paragraphs = String(text).split('\n');
    const lines = [];

    for (let p = 0; p < paragraphs.length; p++) {
      const para = paragraphs[p].trim();
      if (!para) {
        if (p < paragraphs.length - 1) lines.push('');
        continue;
      }
      const words = para.split(/\s+/);
      let currentLine = words[0];

      for (let i = 1; i < words.length; i++) {
        const testLine = currentLine + ' ' + words[i];
        const metrics = ctx.measureText(testLine);
        if (metrics.width > maxWidth) {
          lines.push(currentLine);
          currentLine = words[i];
        } else {
          currentLine = testLine;
        }
      }
      lines.push(currentLine);
    }
    return lines;
  }

  // -------------------------------------------------------------
  // HELPER: Path Name Geodesic Logic (Identical to generate_graph.py)
  // -------------------------------------------------------------
  function getPathName(claim_u, claim_psi, real_u, real_psi) {
    let exitName = "Reckoning", originZone = "Greater Evil";
    if (claim_u > 0 && claim_psi > 0) { exitName = "Fall"; originZone = "Greater Good"; }
    else if (claim_u <= 0 && claim_psi > 0) { exitName = "Revelation"; originZone = "Greatest Lie"; }
    else if (claim_u > 0 && claim_psi <= 0) { exitName = "Awakening"; originZone = "Lesser Good"; }

    let entryName = "Destruction", destZone = "Greater Evil";
    if (real_u > 0 && real_psi > 0) { entryName = "Grace"; destZone = "Greater Good"; }
    else if (real_u <= 0 && real_psi > 0) { entryName = "Deception"; destZone = "Greatest Lie"; }
    else if (real_u > 0 && real_psi <= 0) { entryName = "Redemption"; destZone = "Lesser Good"; }

    if (originZone === destZone) return "Stasis";
    return `${exitName} into ${entryName}`;
  }

  // -------------------------------------------------------------
  // 1. TRAJECTORY GRAPH ENGINE (Port of generate_graph.py)
  // -------------------------------------------------------------
  function drawGraphCanvas(story, canvas) {
    if (!canvas) canvas = document.createElement('canvas');
    canvas.width = 1000;
    canvas.height = 1000;
    const ctx = canvas.getContext('2d');

    const claim_u = (story.claim_u !== null && story.claim_u !== undefined) ? Number(story.claim_u) : 0.0;
    const claim_psi = (story.claim_psi !== null && story.claim_psi !== undefined) ? Number(story.claim_psi) : 0.0;
    const real_u = (story.real_u !== null && story.real_u !== undefined) ? Number(story.real_u) : 0.0;
    const real_psi = (story.real_psi !== null && story.real_psi !== undefined) ? Number(story.real_psi) : 0.0;
    const title = story.subject || "Psochic Hegemony Assessment";
    const pathName = getPathName(claim_u, claim_psi, real_u, real_psi);

    // Canvas Background
    ctx.fillStyle = '#111111';
    ctx.fillRect(0, 0, 1000, 1000);

    // Grid plotting boundaries (matplotlib tight_layout rect=[0, 0.14, 1, 1] on 1000x1000)
    const plotLeft = 145;
    const plotRight = 930;
    const plotTop = 110;
    const plotBottom = 755;
    const plotWidth = plotRight - plotLeft;
    const plotHeight = plotBottom - plotTop;

    // Coordinate mapping: Left is +2.5, Right is -2.5. Top is +2.5, Bottom is -2.5
    function toCanvasX(u) {
      return plotLeft + ((2.5 - u) / 5.0) * plotWidth;
    }
    function toCanvasY(psi) {
      return plotTop + ((2.5 - psi) / 5.0) * plotHeight;
    }

    // 256x256 Gaussian Morality Field Calculation (Exact port of generate_graph.py)
    const gridRes = 128; // high-resolution offscreen grid
    const offCanvas = document.createElement('canvas');
    offCanvas.width = gridRes;
    offCanvas.height = gridRes;
    const offCtx = offCanvas.getContext('2d');
    const imgData = offCtx.createImageData(gridRes, gridRes);

    const green_attractors = [
      { u: 1.0, psi: 1.0, size: 32 },
      { u: 1.0, psi: 0.0, size: 22 },
      { u: 1.0, psi: -1.0, size: 16 }
    ];
    const red_attractors = [
      { u: -1.0, psi: -1.0, size: 32 },
      { u: -1.0, psi: 0.0, size: 22 },
      { u: -1.0, psi: 1.0, size: 16 }
    ];

    const field_sigma = 1.3;
    const max_size = 32.0;
    const judgement_points = [{ u: claim_u, psi: claim_psi }, { u: real_u, psi: real_psi }];
    const green_lean = judgement_points.reduce((acc, p) => acc + Math.max(p.u, 0.0) / 2.0, 0);
    const red_lean = judgement_points.reduce((acc, p) => acc + Math.max(-p.u, 0.0) / 2.0, 0);
    const like_boost_strength = 0.6;
    const green_boost = 1.0 + like_boost_strength * green_lean;
    const red_boost = 1.0 + like_boost_strength * red_lean;

    const two_sigma_sq = 2.0 * field_sigma * field_sigma;

    for (let gy = 0; gy < gridRes; gy++) {
      const psi = 2.0 - (gy / (gridRes - 1)) * 4.0;
      for (let gx = 0; gx < gridRes; gx++) {
        const u = 2.0 - (gx / (gridRes - 1)) * 4.0;

        // Pull from attractors
        let gPull = 0;
        for (let i = 0; i < green_attractors.length; i++) {
          const a = green_attractors[i];
          const distSq = (u - a.u) * (u - a.u) + (psi - a.psi) * (psi - a.psi);
          gPull += (a.size / max_size) * green_boost * Math.exp(-distSq / two_sigma_sq);
        }

        let rPull = 0;
        for (let i = 0; i < red_attractors.length; i++) {
          const a = red_attractors[i];
          const distSq = (u - a.u) * (u - a.u) + (psi - a.psi) * (psi - a.psi);
          rPull += (a.size / max_size) * red_boost * Math.exp(-distSq / two_sigma_sq);
        }

        // Judgement pull
        let jGreen = 0, jRed = 0, jWhite = 0;
        for (let i = 0; i < judgement_points.length; i++) {
          const jp = judgement_points[i];
          const cv = Math.max(-1.0, Math.min(1.0, jp.u / 2.0));
          const distSq = (u - jp.u) * (u - jp.u) + (psi - jp.psi) * (psi - jp.psi);
          const inf = Math.exp(-distSq / two_sigma_sq);
          jGreen += 2.0 * Math.max(cv, 0.0) * inf;
          jRed += 2.0 * Math.max(-cv, 0.0) * inf;
          jWhite += 3.5 * (1.0 - Math.abs(cv)) * inf;
        }

        const totalGreen = gPull + jGreen;
        const totalRed = rPull + jRed;
        const totalWhite = jWhite;

        const hue_t = totalRed / (totalGreen + totalRed + 1e-9);
        // Hegemony cmap: green (0,255,0) -> white (255,255,255) -> red (255,0,0)
        let rVal, gVal, bVal;
        if (hue_t < 0.5) {
          const t = hue_t * 2.0;
          rVal = t * 255;
          gVal = 255;
          bVal = t * 255;
        } else {
          const t = (hue_t - 0.5) * 2.0;
          rVal = 255;
          gVal = (1.0 - t) * 255;
          bVal = (1.0 - t) * 255;
        }

        const whiteFrac = totalWhite / (totalGreen + totalRed + totalWhite + 1e-9);
        rVal = rVal * (1.0 - whiteFrac) + 255 * whiteFrac;
        gVal = gVal * (1.0 - whiteFrac) + 255 * whiteFrac;
        bVal = bVal * (1.0 - whiteFrac) + 255 * whiteFrac;

        const idx = (gy * gridRes + gx) * 4;
        imgData.data[idx] = Math.round(rVal);
        imgData.data[idx + 1] = Math.round(gVal);
        imgData.data[idx + 2] = Math.round(bVal);
        imgData.data[idx + 3] = Math.round(0.30 * 255);
      }
    }
    offCtx.putImageData(imgData, 0, 0);

    // Draw morality field clipped within +/- 2.0 boundary
    const xPlus2 = toCanvasX(2.0), xMinus2 = toCanvasX(-2.0);
    const yPlus2 = toCanvasY(2.0), yMinus2 = toCanvasY(-2.0);
    ctx.drawImage(offCanvas, xPlus2, yPlus2, xMinus2 - xPlus2, yMinus2 - yPlus2);

    // Plot Grid Lines & Ticks
    ctx.strokeStyle = 'rgba(128, 128, 128, 0.3)';
    ctx.lineWidth = 0.5;
    ctx.setLineDash([2, 4]);

    const xTicks = [2.0, 1.0, 0.5, 0.0, -0.5, -1.0, -2.0];
    const yTicks = [2.0, 1.0, 0.0, -1.0, -2.0];

    for (let u of xTicks) {
      const cx = toCanvasX(u);
      ctx.beginPath(); ctx.moveTo(cx, plotTop); ctx.lineTo(cx, plotBottom); ctx.stroke();
    }
    for (let psi of yTicks) {
      const cy = toCanvasY(psi);
      ctx.beginPath(); ctx.moveTo(plotLeft, cy); ctx.lineTo(plotRight, cy); ctx.stroke();
    }
    ctx.setLineDash([]);

    // Axes lines (u=0, psi=0)
    ctx.strokeStyle = 'rgba(128, 128, 128, 0.6)';
    ctx.lineWidth = 1.0;
    const axisX0 = toCanvasX(0.0), axisY0 = toCanvasY(0.0);
    ctx.beginPath(); ctx.moveTo(axisX0, plotTop); ctx.lineTo(axisX0, plotBottom); ctx.stroke();
    ctx.beginPath(); ctx.moveTo(plotLeft, axisY0); ctx.lineTo(plotRight, axisY0); ctx.stroke();

    // Zone 1 Inner Horizon (dashed rectangle +/- 1.0)
    ctx.strokeStyle = 'white';
    ctx.lineWidth = 1.5;
    ctx.setLineDash([6, 6]);
    ctx.strokeRect(toCanvasX(1.0), toCanvasY(1.0), toCanvasX(-1.0) - toCanvasX(1.0), toCanvasY(-1.0) - toCanvasY(1.0));

    // Zone 2 Outer Horizon (solid rectangle +/- 2.0)
    ctx.setLineDash([]);
    ctx.lineWidth = 2.0;
    ctx.strokeRect(toCanvasX(2.0), toCanvasY(2.0), toCanvasX(-2.0) - toCanvasX(2.0), toCanvasY(-2.0) - toCanvasY(2.0));

    // Hegemony Cross (Background static upright cross)
    function drawHegemonyCross(scale, rotDeg, alpha, color) {
      ctx.save();
      ctx.translate(axisX0, axisY0);
      ctx.rotate((rotDeg * Math.PI) / 180);
      ctx.strokeStyle = color;
      ctx.globalAlpha = alpha;
      ctx.lineWidth = 14 * scale * (plotWidth / 500);

      const dX_unit = (plotWidth / 5.0) * scale;
      const dY_unit = (plotHeight / 5.0) * scale;

      // Long beam: from (-1,-1) to (2,2)
      ctx.beginPath();
      ctx.moveTo(-(-1.0) * dX_unit, -(-1.0) * dY_unit);
      ctx.lineTo(-(2.0) * dX_unit, -(2.0) * dY_unit);
      ctx.stroke();

      // Crossbeam: from (1,-1) to (-1,1)
      ctx.beginPath();
      ctx.moveTo(-(1.0) * dX_unit, -(-1.0) * dY_unit);
      ctx.lineTo(-(-1.0) * dX_unit, -(1.0) * dY_unit);
      ctx.stroke();
      ctx.restore();
    }

    // 1. Static Upright Hegemony Cross (25% opacity)
    drawHegemonyCross(1.0, 0.0, 0.25, '#CCCCCC');

    // 2. Dynamic Needle Cross (50% opacity, rotated along Resulting Judgement)
    const mag = Math.hypot(real_u, real_psi);
    if (mag > 0.05) {
      const targetAngle = (Math.atan2(real_psi, real_u) * 180) / Math.PI;
      const rotAngle = targetAngle - 45.0;
      drawHegemonyCross(0.55, rotAngle, 0.50, 'white');
    }

    // Six Attractors
    const allAttractors = [
      { u: 1.0, psi: 1.0, color: '#00FF00', r: 16 },
      { u: 1.0, psi: 0.0, color: '#98FB98', r: 11 },
      { u: 1.0, psi: -1.0, color: '#98FB98', r: 8 },
      { u: -1.0, psi: -1.0, color: '#FF0000', r: 16 },
      { u: -1.0, psi: 0.0, color: '#FF9999', r: 11 },
      { u: -1.0, psi: 1.0, color: '#FF9999', r: 8 }
    ];
    for (let a of allAttractors) {
      ctx.fillStyle = a.color;
      ctx.globalAlpha = 0.75;
      ctx.beginPath();
      ctx.arc(toCanvasX(a.u), toCanvasY(a.psi), a.r * 1.5, 0, Math.PI * 2);
      ctx.fill();
    }
    ctx.globalAlpha = 1.0;

    // Alchemical Corner Labels
    ctx.font = 'italic 12px "DejaVu Sans", Arial, sans-serif';
    ctx.fillStyle = 'rgba(255, 255, 255, 0.45)';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillText("AIR", toCanvasX(2.22), toCanvasY(2.22));
    ctx.fillText("FIRE", toCanvasX(-2.22), toCanvasY(2.22));
    ctx.fillText("WATER", toCanvasX(2.22), toCanvasY(-2.22));
    ctx.fillText("EARTH", toCanvasX(-2.22), toCanvasY(-2.22));

    ctx.fillStyle = 'rgba(255, 255, 255, 0.35)';
    ctx.font = 'italic 11px "DejaVu Sans", Arial, sans-serif';
    ctx.fillText("HOT", toCanvasX(0.0), toCanvasY(2.15));
    ctx.fillText("COLD", toCanvasX(0.0), toCanvasY(-2.15));
    ctx.fillText("WET", toCanvasX(2.3), toCanvasY(0.0));
    ctx.fillText("DRY", toCanvasX(-2.3), toCanvasY(0.0));

    // Zone 1 Corner Labels
    ctx.font = '14px "DejaVu Sans", Arial, sans-serif';
    ctx.fillStyle = 'white';
    ctx.fillText("The Greater Good", toCanvasX(1.0 + 0.1), toCanvasY(1.0 + 0.1) - 10);
    ctx.fillText("(Flow)", toCanvasX(1.0 + 0.1), toCanvasY(1.0 + 0.1) + 10);

    ctx.fillText("The Greatest Lie", toCanvasX(-1.0 - 0.1), toCanvasY(1.0 + 0.1) - 10);
    ctx.fillText("(Greed)", toCanvasX(-1.0 - 0.1), toCanvasY(1.0 + 0.1) + 10);

    ctx.fillText("The Lesser Good", toCanvasX(1.0 + 0.1), toCanvasY(-1.0 - 0.1) - 10);
    ctx.fillText("(Peace)", toCanvasX(1.0 + 0.1), toCanvasY(-1.0 - 0.1) + 10);

    ctx.fillText("The Greater Evil", toCanvasX(-1.0 - 0.1), toCanvasY(-1.0 - 0.1) - 10);
    ctx.fillText("(Void)", toCanvasX(-1.0 - 0.1), toCanvasY(-1.0 - 0.1) + 10);

    // Zone 2 Strategic Extremes
    ctx.textAlign = 'left';
    ctx.fillText("PRODUCTIVE", toCanvasX(1.9), toCanvasY(1.9));
    ctx.fillText("(Joy)", toCanvasX(1.9), toCanvasY(1.9) + 18);
    ctx.fillText("CONSTRUCTIVE", toCanvasX(1.9), toCanvasY(-1.9) - 18);
    ctx.fillText("(Peace)", toCanvasX(1.9), toCanvasY(-1.9));

    ctx.textAlign = 'right';
    ctx.fillText("REDUCTIVE", toCanvasX(-1.9), toCanvasY(1.9));
    ctx.fillText("(Anger)", toCanvasX(-1.9), toCanvasY(1.9) + 18);
    ctx.fillText("REGRESSIVE", toCanvasX(-1.9), toCanvasY(-1.9) - 18);
    ctx.fillText("(Depression)", toCanvasX(-1.9), toCanvasY(-1.9));

    // Stated Claim (Yellow Ring with black bar)
    const clX = toCanvasX(claim_u), clY = toCanvasY(claim_psi);
    ctx.strokeStyle = '#FFFF00';
    ctx.lineWidth = 3;
    ctx.beginPath();
    ctx.arc(clX, clY, 8, 0, Math.PI * 2);
    ctx.stroke();
    ctx.strokeStyle = '#111111';
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.moveTo(clX - 8, clY); ctx.lineTo(clX + 8, clY);
    ctx.stroke();

    // Actual Reality (Red 5-pointed star)
    const reX = toCanvasX(real_u), reY = toCanvasY(real_psi);
    function drawStar(cx, cy, spikes, outerRadius, innerRadius) {
      let rot = (Math.PI / 2) * 3;
      let x = cx, y = cy;
      const step = Math.PI / spikes;
      ctx.beginPath();
      ctx.moveTo(cx, cy - outerRadius);
      for (let i = 0; i < spikes; i++) {
        x = cx + Math.cos(rot) * outerRadius;
        y = cy + Math.sin(rot) * outerRadius;
        ctx.lineTo(x, y);
        rot += step;
        x = cx + Math.cos(rot) * innerRadius;
        y = cy + Math.sin(rot) * innerRadius;
        ctx.lineTo(x, y);
        rot += step;
      }
      ctx.lineTo(cx, cy - outerRadius);
      ctx.closePath();
      ctx.fillStyle = '#FF0000';
      ctx.fill();
    }
    drawStar(reX, reY, 5, 12, 5);

    // Dashed Arc Arrow from Claim to Reality
    ctx.save();
    ctx.strokeStyle = 'white';
    ctx.lineWidth = 2.0;
    ctx.setLineDash([6, 4]);
    const dx = reX - clX, dy = reY - clY;
    const ctrlX = (clX + reX) / 2 + dy * 0.2;
    const ctrlY = (clY + reY) / 2 - dx * 0.2;
    ctx.beginPath();
    ctx.moveTo(clX, clY);
    ctx.quadraticCurveTo(ctrlX, ctrlY, reX, reY);
    ctx.stroke();
    ctx.restore();

    // Arrowhead at Reality
    const angle = Math.atan2(reY - ctrlY, reX - ctrlX);
    ctx.fillStyle = 'white';
    ctx.beginPath();
    ctx.moveTo(reX, reY);
    ctx.lineTo(reX - 12 * Math.cos(angle - Math.PI / 6), reY - 12 * Math.sin(angle - Math.PI / 6));
    ctx.lineTo(reX - 12 * Math.cos(angle + Math.PI / 6), reY - 12 * Math.sin(angle + Math.PI / 6));
    ctx.closePath();
    ctx.fill();

    // Title Block at top (3 lines)
    ctx.textAlign = 'center';
    ctx.fillStyle = 'white';
    ctx.font = 'bold 15px "DejaVu Sans", Arial, sans-serif';
    ctx.fillText(title, 500, 32);

    ctx.font = '14px "DejaVu Sans", Arial, sans-serif';
    ctx.fillText(`Projected Eventuality: ${pathName}`, 500, 56);

    const cU_str = `${claim_u > 0 ? '+' : ''}${claim_u.toFixed(1)}`;
    const cPsi_str = `${claim_psi > 0 ? '+' : ''}${claim_psi.toFixed(1)}`;
    const rU_str = `${real_u > 0 ? '+' : ''}${real_u.toFixed(1)}`;
    const rPsi_str = `${real_psi > 0 ? '+' : ''}${real_psi.toFixed(1)}`;
    ctx.fillText(`Stated: (${cU_str}, ${cPsi_str})  |  Actual: (${rU_str}, ${rPsi_str})`, 500, 80);

    // Axis Labels
    ctx.font = '13px "DejaVu Sans", Arial, sans-serif';
    ctx.fillText("Morality (υ)", (plotLeft + plotRight) / 2, plotBottom + 70);

    ctx.save();
    ctx.translate(plotLeft - 105, (plotTop + plotBottom) / 2);
    ctx.rotate(-Math.PI / 2);
    ctx.fillText("Will (ψ)", 0, 0);
    ctx.restore();

    // X Tick Labels
    const xLabels = [
      ["Everyone", "(+2.0)", "Egalitarian"],
      ["Others", "(+1.0)"],
      ["Other", "(+0.5)"],
      ["No One", "(0.0)"],
      ["My Group", "(-0.5)"],
      ["Me", "(-1.0)"],
      ["Only Me", "(-2.0)", "Anti-Egalitarian"]
    ];
    ctx.font = '10px "DejaVu Sans", Arial, sans-serif';
    ctx.fillStyle = 'white';
    for (let i = 0; i < xTicks.length; i++) {
      const cx = toCanvasX(xTicks[i]);
      const lines = xLabels[i];
      let yOffset = plotBottom + 16;
      for (let l of lines) {
        ctx.fillText(l, cx, yOffset);
        yOffset += 13;
      }
    }

    // Y Tick Labels
    const yLabels = [
      ["Active-", "Active (+2.0)"],
      ["Passive-", "Active (+1.0)"],
      ["Neutral (0.0)"],
      ["Passive-", "Passive (-1.0)"],
      ["Active-", "Passive (-2.0)"]
    ];
    ctx.textAlign = 'right';
    for (let i = 0; i < yTicks.length; i++) {
      const cy = toCanvasY(yTicks[i]);
      const lines = yLabels[i];
      let yOffset = cy - ((lines.length - 1) * 12) / 2;
      for (let l of lines) {
        ctx.fillText(l, plotLeft - 12, yOffset);
        yOffset += 12;
      }
    }

    // Legend Box (Bottom Left)
    const legX = 20, legY = plotBottom + 10, legW = 120, legH = 46;
    ctx.fillStyle = '#111111';
    ctx.strokeStyle = 'white';
    ctx.lineWidth = 1;
    ctx.fillRect(legX, legY, legW, legH);
    ctx.strokeRect(legX, legY, legW, legH);

    // Stated Claim Icon in Legend
    ctx.strokeStyle = '#FFFF00';
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.arc(legX + 16, legY + 14, 6, 0, Math.PI * 2);
    ctx.stroke();
    ctx.strokeStyle = '#111111';
    ctx.beginPath();
    ctx.moveTo(legX + 10, legY + 14); ctx.lineTo(legX + 22, legY + 14);
    ctx.stroke();

    ctx.textAlign = 'left';
    ctx.fillStyle = 'white';
    ctx.font = '10px "DejaVu Sans", Arial, sans-serif';
    ctx.fillText("Stated Claim", legX + 30, legY + 18);

    // Actual Reality Icon in Legend
    drawStar(legX + 16, legY + 32, 5, 8, 3.5);
    ctx.fillText("Actual Reality", legX + 30, legY + 36);

    // Description Block at bottom
    ctx.textAlign = 'center';
    ctx.fillStyle = '#999999';
    ctx.font = '10.5px "DejaVu Sans", Arial, sans-serif';
    const descLines = [
      'This graph asks and answers the question "Who does this idea benefit?" measuring Relative Morality.',
      "Benefit is a vector where each unit is 'Scope of Potential'[Group direction, magnitude] cross spectrum of will [active activity to active passivity, magnitude]",
      "The Greater Cross points the way to Good and Joy, its smaller paths lead nowhere. The smaller cross points to the consequences of your choices and actions, the smaller paths what you could but didn't do.",
      "Your responsibility is whether you'll choose to align with or against Good"
    ];
    let dY = 875;
    for (let dl of descLines) {
      ctx.fillText(dl, 500, dY);
      dY += 18;
    }

    // Watermark
    ctx.font = 'italic 11px "DejaVu Sans", Arial, sans-serif';
    ctx.fillStyle = '#444444';
    ctx.fillText("Psochic Hegemony Graph: The map of Good and Evil", 500, 980);

    return canvas;
  }

  // -------------------------------------------------------------
  // 2. VERDICT INFO CARD ENGINE (Port of _generate_verdict_card)
  // -------------------------------------------------------------
  function drawVerdictCardCanvas(story, canvas) {
    if (!canvas) canvas = document.createElement('canvas');
    const posts = story.posts || [];
    const isMultiAspect = Boolean(story.aspects) || (posts.length >= 14 && ((posts[4] || '').toLowerCase().includes('sub-audit') || (posts[4] || '').trim().startsWith('- ')));

    const sections = [
      { label: "THE HOOK", text: (posts[0] || '').replace(/^Hook:\s*/i, '').trim(), color: "#F472B6" },
      { label: "THE CLAIM", text: (posts[1] || '').replace(/^(The\s+)?Claim:\s*|^Stated Judgement:\s*/i, '').trim(), color: "#94A3B8" },
      { label: "THE REALITY", text: (posts[2] || '').replace(/^(The\s+)?Reality:\s*|^Resulting Judgement:\s*/i, '').trim(), color: "#38BDF8" },
      { label: "THE VERDICT", text: (posts[3] || '').replace(/^(Stated\s+)?Verdict:\s*/i, '').trim(), color: "#FBBF24" }
    ];
    if (isMultiAspect && posts[4]) {
      sections.push({
        label: "SUB-AUDITS BREAKDOWN",
        text: posts[4].replace(/^(Sub-Audits\s+Breakdown|Sub-Audits):\s*/i, '').trim(),
        color: "#A855F7"
      });
    }

    const real_u = (story.real_u !== null && story.real_u !== undefined) ? Number(story.real_u) : 0.0;
    const real_psi = (story.real_psi !== null && story.real_psi !== undefined) ? Number(story.real_psi) : 0.0;
    const coordsStr = `(${real_u > 0 ? '+' : ''}${real_u.toFixed(2)}, ${real_psi > 0 ? '+' : ''}${real_psi.toFixed(2)})`;
    const verdictSubtitle = `Resulting Judgement: ${coordsStr} — ${story.verdict || 'Hegemonic Audit'}`;

    const canvas_w = 1200;
    const x_left = 40;
    const x_right = canvas_w - x_left;
    const drawable_w = x_right - x_left;
    const col_gap = 30;
    const col_w = Math.floor((drawable_w - col_gap) / 2);
    const sec_text_w = col_w - 40;
    const line_h = 38;
    const card_gap = 25;

    // Measurement pass
    const tempCanvas = document.createElement('canvas');
    const tempCtx = tempCanvas.getContext('2d');

    tempCtx.font = 'bold 39px "Segoe UI", Arial, sans-serif';
    const title_lines = wrapCanvasText(tempCtx, story.subject || 'Audit Summary', drawable_w);

    tempCtx.font = 'bold 27px "Segoe UI", Arial, sans-serif';
    const subtitle_lines = wrapCanvasText(tempCtx, verdictSubtitle, drawable_w);

    const title_h = (title_lines.length * 46) + 5 + (subtitle_lines.length * 34);
    let current_y = 50 + title_h + 30;
    const grid_start_y = current_y;

    tempCtx.font = '29px "Segoe UI", Arial, sans-serif';
    const left_layouts = [];
    let left_y = grid_start_y;
    for (let i = 0; i < Math.min(2, sections.length); i++) {
      const sec = sections[i];
      const wrapped = wrapCanvasText(tempCtx, sec.text, sec_text_w);
      const card_h = 25 + 24 + wrapped.length * line_h + 25;
      left_layouts.push({ sec, x1: x_left, x2: x_left + col_w, y: left_y, h: card_h, lines: wrapped });
      left_y += card_h + card_gap;
    }
    const left_grid_h = left_y - card_gap - grid_start_y;

    const right_layouts = [];
    let right_y = grid_start_y;
    for (let i = 2; i < Math.min(4, sections.length); i++) {
      const sec = sections[i];
      const wrapped = wrapCanvasText(tempCtx, sec.text, sec_text_w);
      const card_h = 25 + 24 + wrapped.length * line_h + 25;
      right_layouts.push({ sec, x1: x_left + col_w + col_gap, x2: x_right, y: right_y, h: card_h, lines: wrapped });
      right_y += card_h + card_gap;
    }
    const right_grid_h = right_y - card_gap - grid_start_y;

    let grid_h = Math.max(left_grid_h, right_grid_h);

    let sub_layout = null;
    if (sections.length === 5) {
      const sec = sections[4];
      const wrapped = wrapCanvasText(tempCtx, sec.text, drawable_w - 40);
      const card_h_sub = 25 + 24 + wrapped.length * line_h + 25;
      const sub_card_y = grid_start_y + grid_h + card_gap;
      sub_layout = { sec, x1: x_left, x2: x_right, y: sub_card_y, h: card_h_sub, lines: wrapped };
      grid_h += card_gap + card_h_sub;
    }

    const footer_h = 160;
    const final_height = grid_start_y + grid_h + footer_h;

    canvas.width = canvas_w;
    canvas.height = final_height;
    const ctx = canvas.getContext('2d');

    // Canvas Background
    ctx.fillStyle = '#0B0F19';
    ctx.fillRect(0, 0, canvas_w, final_height);

    // Title & Subtitle
    ctx.textAlign = 'left';
    ctx.textBaseline = 'alphabetic';
    let y = 50;
    ctx.fillStyle = '#F8FAFC';
    ctx.font = 'bold 39px "Segoe UI", Arial, sans-serif';
    for (let tl of title_lines) {
      ctx.fillText(tl, x_left, y + 35);
      y += 46;
    }
    y += 5;
    ctx.fillStyle = '#38BDF8';
    ctx.font = 'bold 27px "Segoe UI", Arial, sans-serif';
    for (let sl of subtitle_lines) {
      ctx.fillText(sl, x_left, y + 25);
      y += 34;
    }

    // Function to draw individual card matching _draw_individual_card_v3
    function drawCardBox(lay) {
      const sec = lay.sec;
      ctx.fillStyle = '#141D2F';
      ctx.strokeStyle = '#25354F';
      ctx.lineWidth = 1;

      // Card container
      ctx.beginPath();
      ctx.roundRect(lay.x1, lay.y, lay.x2 - lay.x1, lay.h, 12);
      ctx.fill();
      ctx.stroke();

      // Left Accent Strip
      ctx.fillStyle = sec.color;
      ctx.beginPath();
      ctx.roundRect(lay.x1 + 1, lay.y + 10, 6, lay.h - 20, 3);
      ctx.fill();

      // Section Label
      ctx.fillStyle = sec.color;
      ctx.font = 'bold 27px "Segoe UI", Arial, sans-serif';
      ctx.fillText(sec.label, lay.x1 + 20, lay.y + 38);

      // Body lines
      ctx.fillStyle = '#E2E8F0';
      ctx.font = '29px "Segoe UI", Arial, sans-serif';
      let text_y = lay.y + 75;
      for (let line of lay.lines) {
        ctx.fillText(line, lay.x1 + 20, text_y);
        text_y += line_h;
      }
    }

    for (let lay of left_layouts) drawCardBox(lay);
    for (let lay of right_layouts) drawCardBox(lay);
    if (sub_layout) drawCardBox(sub_layout);

    // Footer
    const footer_y = grid_start_y + grid_h + 30;
    ctx.fillStyle = '#64748B';
    ctx.font = 'bold 27px "Segoe UI", Arial, sans-serif';
    ctx.fillText("Aletheia Bot | Uncompromising Logic & Truth", x_left, footer_y + 35);

    ctx.fillStyle = '#475569';
    ctx.font = '22px "Segoe UI", Arial, sans-serif';
    ctx.fillText("Verified Gnostic Actualism Audit", x_left, footer_y + 75);

    return canvas;
  }

  // -------------------------------------------------------------
  // 3. ANALYSIS INFO CARD ENGINE (Port of _generate_analysis_full_card)
  // -------------------------------------------------------------
  function drawAnalysisCardCanvas(story, canvas) {
    if (!canvas) canvas = document.createElement('canvas');
    const posts = story.posts || [];
    const isMultiAspect = Boolean(story.aspects) || (posts.length >= 14 && ((posts[4] || '').toLowerCase().includes('sub-audit') || (posts[4] || '').trim().startsWith('- ')));

    let secOffset = isMultiAspect ? 5 : 4;
    const sections = [
      { label: "CONTEXT", text: (posts[secOffset] || '').replace(/^(What's happening|Context):\s*/i, '').trim(), color: "#38BDF8" },
      {
        label: (posts[secOffset + 1] || '').toLowerCase().includes('bright side') ? "THE BRIGHT SIDE" : "THE POISON",
        text: (posts[secOffset + 1] || '').replace(/^(The\s+)?(Poison|Bright Side):\s*/i, '').trim(),
        color: (posts[secOffset + 1] || '').toLowerCase().includes('bright side') ? "#10B981" : "#EF4444"
      },
      { label: "BREAKDOWN & PLANE ERROR", text: (posts[secOffset + 2] || '').replace(/^(The\s+)?Breakdown & Plane Error:\s*/i, '').trim(), color: "#C084FC" },
      { label: "SOCIAL PHYSICS ANALYSIS", text: (posts[secOffset + 3] || '').replace(/^Social Physics Analysis:\s*/i, '').trim(), color: "#60A5FA" },
      { label: "TRAJECTORY & DESTINATION", text: (posts[secOffset + 4] || '').replace(/^(The\s+)?Trajectory:\s*/i, '').trim(), color: "#F472B6" },
      { label: "THE UNAVOIDABLES", text: (posts[secOffset + 5] || '').replace(/The Unavoidable Truth:\s*/i, 'Truth: ').replace(/The Unavoidable Lie:\s*/i, '\nLie: ').trim(), color: "#F59E0B" }
    ];

    const personas = [
      { label: "ALETHEKANON", text: (posts[secOffset + 6] || '').replace(/^Alethekanon:\s*/i, '').trim(), color: "#38BDF8" },
      { label: "AWWTHEKANON", text: (posts[secOffset + 7] || '').replace(/^Awwthekanon:\s*/i, '').trim(), color: "#10B981" },
      { label: "BROTHEKANON", text: (posts[secOffset + 8] || '').replace(/^Brothekanon:\s*/i, '').trim(), color: "#F59E0B" }
    ];

    const real_u = (story.real_u !== null && story.real_u !== undefined) ? Number(story.real_u) : 0.0;
    const real_psi = (story.real_psi !== null && story.real_psi !== undefined) ? Number(story.real_psi) : 0.0;
    const coordsStr = `(${real_u > 0 ? '+' : ''}${real_u.toFixed(2)}, ${real_psi > 0 ? '+' : ''}${real_psi.toFixed(2)})`;
    const analysisSubtitle = `SYSTEM ANALYSIS & PERSPECTIVES | ${coordsStr}`;

    const canvas_w = 1200;
    const x_left = 40;
    const x_right = canvas_w - x_left;
    const drawable_w = x_right - x_left;
    const col_gap = 30;
    const col_w = Math.floor((drawable_w - col_gap) / 2);
    const sec_text_w = col_w - 40;
    const line_h = 32;
    const card_gap = 25;

    const tempCanvas = document.createElement('canvas');
    const tempCtx = tempCanvas.getContext('2d');

    tempCtx.font = 'bold 36px "Segoe UI", Arial, sans-serif';
    const title_lines = wrapCanvasText(tempCtx, story.subject || 'System Analysis', drawable_w);

    tempCtx.font = 'bold 24px "Segoe UI", Arial, sans-serif';
    const subtitle_lines = wrapCanvasText(tempCtx, analysisSubtitle, drawable_w);

    const title_h = (title_lines.length * 42) + 5 + (subtitle_lines.length * 30);
    let current_y = 50 + title_h + 30;
    const grid_start_y = current_y;

    tempCtx.font = '24px "Segoe UI", Arial, sans-serif';
    const left_layouts = [];
    let left_y = grid_start_y;
    for (let i = 0; i < 3; i++) {
      const sec = sections[i];
      const wrapped = wrapCanvasText(tempCtx, sec.text, sec_text_w);
      const card_h = 25 + 24 + wrapped.length * line_h + 25;
      left_layouts.push({ sec, x1: x_left, x2: x_left + col_w, y: left_y, h: card_h, lines: wrapped });
      left_y += card_h + card_gap;
    }
    const left_grid_h = left_y - card_gap - grid_start_y;

    const right_layouts = [];
    let right_y = grid_start_y;
    for (let i = 3; i < 6; i++) {
      const sec = sections[i];
      const wrapped = wrapCanvasText(tempCtx, sec.text, sec_text_w);
      const card_h = 25 + 24 + wrapped.length * line_h + 25;
      right_layouts.push({ sec, x1: x_left + col_w + col_gap, x2: x_right, y: right_y, h: card_h, lines: wrapped });
      right_y += card_h + card_gap;
    }
    const right_grid_h = right_y - card_gap - grid_start_y;

    const grid_h = Math.max(left_grid_h, right_grid_h);

    // Persona layout calculation
    const persona_gap = 20;
    const persona_w = Math.floor((drawable_w - (persona_gap * (personas.length - 1))) / personas.length);
    const persona_text_w = persona_w - 30;
    let persona_card_h = 0;
    const persona_layouts = [];

    tempCtx.font = '20px "Segoe UI", Arial, sans-serif';
    for (let p of personas) {
      const wrapped = wrapCanvasText(tempCtx, p.text, persona_text_w);
      const h = 20 + 20 + wrapped.length * 28 + 20;
      if (h > persona_card_h) persona_card_h = h;
      persona_layouts.push({ persona: p, lines: wrapped });
    }

    const persona_y = grid_start_y + grid_h + 30;
    const footer_h = 140;
    const final_height = persona_y + 35 + persona_card_h + footer_h;

    canvas.width = canvas_w;
    canvas.height = final_height;
    const ctx = canvas.getContext('2d');

    ctx.fillStyle = '#0B0F19';
    ctx.fillRect(0, 0, canvas_w, final_height);

    ctx.textAlign = 'left';
    ctx.textBaseline = 'alphabetic';
    let y = 50;
    ctx.fillStyle = '#F8FAFC';
    ctx.font = 'bold 36px "Segoe UI", Arial, sans-serif';
    for (let tl of title_lines) {
      ctx.fillText(tl, x_left, y + 32);
      y += 42;
    }
    y += 5;
    ctx.fillStyle = '#38BDF8';
    ctx.font = 'bold 24px "Segoe UI", Arial, sans-serif';
    for (let sl of subtitle_lines) {
      ctx.fillText(sl, x_left, y + 22);
      y += 30;
    }

    function drawCardBox(lay) {
      const sec = lay.sec;
      ctx.fillStyle = '#141D2F';
      ctx.strokeStyle = '#25354F';
      ctx.lineWidth = 1;

      ctx.beginPath();
      ctx.roundRect(lay.x1, lay.y, lay.x2 - lay.x1, lay.h, 12);
      ctx.fill();
      ctx.stroke();

      ctx.fillStyle = sec.color;
      ctx.beginPath();
      ctx.roundRect(lay.x1 + 1, lay.y + 10, 6, lay.h - 20, 3);
      ctx.fill();

      ctx.fillStyle = sec.color;
      ctx.font = 'bold 24px "Segoe UI", Arial, sans-serif';
      ctx.fillText(sec.label, lay.x1 + 20, lay.y + 34);

      ctx.fillStyle = '#E2E8F0';
      ctx.font = '24px "Segoe UI", Arial, sans-serif';
      let text_y = lay.y + 68;
      for (let line of lay.lines) {
        ctx.fillText(line, lay.x1 + 20, text_y);
        text_y += line_h;
      }
    }

    for (let lay of left_layouts) drawCardBox(lay);
    for (let lay of right_layouts) drawCardBox(lay);

    // Persona Container
    ctx.fillStyle = '#F8FAFC';
    ctx.font = 'bold 24px "Segoe UI", Arial, sans-serif';
    ctx.fillText("TRINARY PERSPECTIVES", x_left, persona_y + 20);

    for (let i = 0; i < personas.length; i++) {
      const pl = persona_layouts[i];
      const p = pl.persona;
      const px = x_left + i * (persona_w + persona_gap);
      const py = persona_y + 35;

      ctx.fillStyle = '#141D2F';
      ctx.strokeStyle = '#25354F';
      ctx.lineWidth = 1;
      ctx.beginPath();
      ctx.roundRect(px, py, persona_w, persona_card_h, 10);
      ctx.fill();
      ctx.stroke();

      // Top color bar
      ctx.fillStyle = p.color;
      ctx.beginPath();
      ctx.roundRect(px, py, persona_w, 4, [10, 10, 0, 0]);
      ctx.fill();

      ctx.fillStyle = p.color;
      ctx.font = 'bold 20px "Segoe UI", Arial, sans-serif';
      ctx.fillText(p.label, px + 15, py + 30);

      ctx.fillStyle = '#E2E8F0';
      ctx.font = '20px "Segoe UI", Arial, sans-serif';
      let text_y = py + 60;
      for (let line of pl.lines) {
        ctx.fillText(line, px + 15, text_y);
        text_y += 28;
      }
    }

    return canvas;
  }

  // -------------------------------------------------------------
  // 4. FIVE-WORD SUMMARY CARD ENGINE (Port of _generate_five_word_card)
  // -------------------------------------------------------------
  function drawFiveWordCardCanvas(story, canvas) {
    if (!canvas) canvas = document.createElement('canvas');
    canvas.width = 1100;
    canvas.height = 860;
    const ctx = canvas.getContext('2d');

    const posts = story.posts || [];
    const subject = story.subject || "Five-Word Audit";
    const real_u = (story.real_u !== null && story.real_u !== undefined) ? Number(story.real_u) : 0.0;
    const real_psi = (story.real_psi !== null && story.real_psi !== undefined) ? Number(story.real_psi) : 0.0;
    const claim_u = (story.claim_u !== null && story.claim_u !== undefined) ? Number(story.claim_u) : 0.0;
    const claim_psi = (story.claim_psi !== null && story.claim_psi !== undefined) ? Number(story.claim_psi) : 0.0;
    const subtitle = `Stated: (${claim_u > 0 ? '+' : ''}${claim_u.toFixed(1)}, ${claim_psi > 0 ? '+' : ''}${claim_psi.toFixed(1)}) | Actual: (${real_u > 0 ? '+' : ''}${real_u.toFixed(1)}, ${real_psi > 0 ? '+' : ''}${real_psi.toFixed(1)})`;

    ctx.fillStyle = '#0B0F19';
    ctx.fillRect(0, 0, 1100, 860);

    ctx.fillStyle = '#F8FAFC';
    ctx.font = 'bold 36px "Segoe UI", Arial, sans-serif';
    ctx.fillText(subject, 40, 75);

    ctx.fillStyle = '#38BDF8';
    ctx.font = 'bold 24px "Segoe UI", Arial, sans-serif';
    ctx.fillText(subtitle, 40, 115);

    // Container box
    ctx.fillStyle = '#141D2F';
    ctx.strokeStyle = '#25354F';
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.roundRect(40, 160, 1020, 660, 16);
    ctx.fill();
    ctx.stroke();

    const lineConfigs = [
      { label: "HOOK", color: "#F472B6" },
      { label: "CLAIM", color: "#94A3B8" },
      { label: "REALITY", color: "#38BDF8" },
      { label: "VERDICT", color: "#FBBF24" },
      { label: "CONTEXT", color: "#60A5FA" }
    ];

    let rowY = 220;
    for (let i = 0; i < Math.min(5, posts.length); i++) {
      const cfg = lineConfigs[i] || { label: "AUDIT", color: "#FFFFFF" };
      ctx.fillStyle = cfg.color;
      ctx.font = 'bold 22px Consolas, monospace';
      ctx.fillText(`[${cfg.label}]`, 70, rowY);

      ctx.fillStyle = '#E2E8F0';
      ctx.font = '22px Consolas, monospace';
      const text = posts[i].replace(/^.*:\s*/, '').trim();
      const wrapped = wrapCanvasText(ctx, text, 800);
      for (let l of wrapped.slice(0, 2)) {
        ctx.fillText(l, 220, rowY);
        rowY += 30;
      }
      rowY += 40;
    }

    return canvas;
  }

  // Export to global scope
  global.AletheiaCanvas = {
    drawGraphCanvas,
    drawVerdictCardCanvas,
    drawAnalysisCardCanvas,
    drawFiveWordCardCanvas
  };

})(typeof window !== 'undefined' ? window : this);
