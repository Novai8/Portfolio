/**
 * scenes2.mjs — offline renderers for scenes 10–18 + end card.
 * Each export: (ctx, L, t) where L = scene-local seconds, t = global seconds.
 */
import {
  W, H, anchorLocal, beat, easeOut, easeOutBack, hash, lerp, clamp01,
  rgba, rr, panel, txt, typed, star, heart, note, measure,
} from './lib.mjs';

const A = anchorLocal;

// ---------------------------------------------------------------- SCENE 10
export function s10(ctx, L, t) {
  const end = 14.5;
  const zoom = clamp01((L - (end - 0.9)) / 0.9);
  const aWalk = A(10, 'walk');
  const aDanger = A(10, 'danger');
  const aRing = A(10, 'ring');

  ctx.save();
  if (zoom > 0) {
    ctx.translate(W * 0.54, H * 0.6);
    ctx.scale(1 + zoom * 1.4, 1 + zoom * 1.4);
    ctx.translate(-W * 0.54, -H * 0.6);
  }

  // iso floor
  ctx.save();
  const g = ctx.createLinearGradient(0, 0, 0, H);
  g.addColorStop(0, '#0e1830'); g.addColorStop(1, '#0a1020');
  ctx.fillStyle = g; ctx.fillRect(0, 0, W, H);
  ctx.strokeStyle = 'rgba(122,208,255,0.13)';
  ctx.lineWidth = 1.5;
  const off = (L * 16) % 90;
  for (let i = -14; i < 22; i++) {
    ctx.beginPath();
    ctx.moveTo(W / 2 + (i * 90 - off) * 0.25, 330);
    ctx.lineTo(W / 2 + (i * 90 - off) * 2.4, H);
    ctx.stroke();
  }
  for (let i = 0; i < 12; i++) {
    const yy = 330 + Math.pow(i + off / 90, 1.7) * 42;
    ctx.beginPath(); ctx.moveTo(0, yy); ctx.lineTo(W, yy); ctx.stroke();
  }
  ctx.restore();

  // labels LIVING = OFFICE = DINING
  ['LIVING', 'OFFICE', 'DINING'].forEach((r2, i) => {
    const p = easeOutBack(beat(L, aWalk + 0.3 + i * 0.55, 0.5));
    if (p <= 0) return;
    ctx.save();
    ctx.globalAlpha = 0.25 + 0.75 * p;
    ctx.translate(395 + i * 405, 108 + (1 - p) * -30);
    ctx.scale(0.8 + 0.2 * p, 0.8 + 0.2 * p);
    ctx.setLineDash([8, 6]);
    ctx.strokeStyle = '#7ad0ff';
    ctx.lineWidth = 3;
    rr(ctx, -128, -34, 256, 62, 14); ctx.stroke();
    ctx.setLineDash([]);
    txt(ctx, r2, 0, 10, { size: 30, family: 'AB', color: '#bfe8ff' });
    ctx.restore();
    if (i < 2) {
      const pp = beat(L, aWalk + 0.6 + i * 0.55, 0.4);
      if (pp > 0) txt(ctx, '=', 600 + i * 402, 116, { size: 44, family: 'AB', color: '#7ad0ff', alpha: pp });
    }
  });

  // couch → desk morph
  if (L > aWalk + 1.2) {
    const pop = beat(L, aWalk + 1.2, 0.4);
    const m = clamp01((L - aWalk - 1.4) / 0.9); // 0 couch → 1 desk
    ctx.save();
    ctx.globalAlpha = pop;
    ctx.translate(450, 560);
    if (m < 1) {
      ctx.globalAlpha = pop * (1 - m);
      // couch
      ctx.fillStyle = '#4a5a8f';
      rr(ctx, -110, -40, 220, 60, 16); ctx.fill();
      rr(ctx, -110, -80, 220, 46, 16); ctx.fill();
      rr(ctx, -124, -70, 26, 76, 10); ctx.fill();
      rr(ctx, 98, -70, 26, 76, 10); ctx.fill();
    }
    if (m > 0) {
      ctx.globalAlpha = pop * m;
      // desk with laptop
      ctx.fillStyle = '#7a5a33';
      rr(ctx, -110, -20, 220, 14, 4); ctx.fill();
      ctx.fillRect(-96, -6, 14, 60); ctx.fillRect(82, -6, 14, 60);
      ctx.fillStyle = '#232a4d';
      rr(ctx, -52, -62, 104, 44, 5); ctx.fill();
      ctx.fillStyle = 'rgba(0,229,255,0.8)';
      rr(ctx, -44, -55, 88, 30, 3); ctx.fill();
    }
    ctx.restore();
    txt(ctx, 'couch → desk', 450, 668, { size: 28, family: 'CVB', color: '#9fd8ff', alpha: pop });
  }

  // dining = desk
  if (L > aWalk + 1.8) {
    const p = beat(L, aWalk + 1.8, 0.4);
    ctx.save();
    ctx.globalAlpha = p;
    ctx.translate(1190, 560 + Math.sin(L * 1.4) * 6);
    ctx.fillStyle = '#e8ecf5';
    ctx.beginPath(); ctx.arc(0, 0, 52, 0, Math.PI * 2); ctx.fill();
    ctx.fillStyle = '#ff9a76';
    ctx.beginPath(); ctx.arc(0, 0, 34, 0, Math.PI * 2); ctx.fill();
    ctx.strokeStyle = '#e8ecf5'; ctx.lineWidth = 6; ctx.lineCap = 'round';
    ctx.beginPath(); ctx.moveTo(-84, -30); ctx.lineTo(-84, 30); ctx.stroke();
    ctx.beginPath(); ctx.moveTo(84, -30); ctx.lineTo(84, 30); ctx.stroke();
    ctx.restore();
    txt(ctx, 'dining = desk', 1190, 668, { size: 28, family: 'CVB', color: '#9fd8ff', alpha: p });
  }

  // pacing person
  const pacing = (Math.sin(L * 1.85) + 1) / 2;
  const px = 700 + pacing * 200;
  const dir = Math.cos(L * 1.85) > 0 ? 1 : -1;
  const legSwing = Math.sin(L * 9) * 10;
  ctx.save();
  ctx.translate(px, 730);
  ctx.scale(dir, 1);
  ctx.strokeStyle = '#cfe0ff'; ctx.lineWidth = 6; ctx.lineCap = 'round';
  ctx.beginPath(); ctx.moveTo(0, -46); ctx.lineTo(-legSwing, 0); ctx.stroke();
  ctx.beginPath(); ctx.moveTo(0, -46); ctx.lineTo(legSwing, 0); ctx.stroke();
  ctx.beginPath(); ctx.moveTo(0, -46); ctx.lineTo(0, -88); ctx.stroke();
  ctx.beginPath(); ctx.arc(0, -104, 15, 0, Math.PI * 2);
  ctx.fillStyle = '#cfe0ff'; ctx.fill();
  ctx.restore();
  ctx.setLineDash([6, 8]);
  ctx.strokeStyle = 'rgba(122,208,255,0.3)'; ctx.lineWidth = 2.5;
  ctx.beginPath(); ctx.ellipse(800, 736, 130, 16, 0, 0, Math.PI * 2); ctx.stroke();
  ctx.setLineDash([]);

  // phone
  if (L > aDanger) {
    const pop = easeOutBack(beat(L, aDanger, 0.5));
    ctx.save();
    ctx.translate(W / 2, 330);
    ctx.scale(pop, pop);
    if (pop > 0.9) {
      for (let i = 0; i < 3; i++) {
        const rp = ((L * 0.9 + i * 0.33) % 1);
        ctx.beginPath(); ctx.arc(0, 0, 60 + rp * 120, 0, Math.PI * 2);
        ctx.strokeStyle = `rgba(122,208,255,${0.5 * (1 - rp)})`;
        ctx.lineWidth = 3;
        ctx.stroke();
      }
    }
    ctx.shadowColor = 'rgba(122,208,255,0.5)'; ctx.shadowBlur = 30;
    ctx.fillStyle = '#20304f';
    rr(ctx, -52, -74, 104, 148, 20); ctx.fill();
    ctx.shadowColor = 'transparent';
    ctx.fillStyle = '#0b1225';
    rr(ctx, -40, -62, 80, 100, 10); ctx.fill();
    ctx.strokeStyle = '#7ad0ff'; ctx.lineWidth = 4;
    ctx.beginPath(); ctx.arc(0, 0, 22, Math.PI * 0.15, Math.PI * 0.85, true); ctx.stroke();
    txt(ctx, 'RING RING RING', 0, 108, {
      size: 16, family: 'JBMB', color: '#7ad0ff',
      alpha: Math.floor(L * 3) % 2 === 0 ? 1 : 0.2,
    });
    ctx.restore();
  }
  ctx.restore();

  if (zoom > 0) {
    ctx.fillStyle = `rgba(2,4,10,${zoom * 0.6})`;
    ctx.fillRect(0, 0, W, H);
  }
}

// ---------------------------------------------------------------- SCENE 11
export function s11(ctx, L, t) {
  const end = 35.8;
  const split = clamp01((L - (end - 0.8)) / 0.8);
  const aPlants = A(11, 'plants');
  const aTwelvek = A(11, 'twelvek');
  const aDont = A(11, 'dontship');
  const aVillain = A(11, 'villain');

  // split bg
  const gL = ctx.createLinearGradient(0, 0, W / 2, H);
  gL.addColorStop(0, '#31124a'); gL.addColorStop(1, '#1a0a2e');
  ctx.fillStyle = gL; ctx.fillRect(0, 0, W / 2 + 2, H);
  const gR = ctx.createLinearGradient(W / 2, 0, W, H);
  gR.addColorStop(0, '#0d3b2e'); gR.addColorStop(1, '#07281f');
  ctx.fillStyle = gR; ctx.fillRect(W / 2 - 2, 0, W / 2 + 2, H);
  ctx.fillStyle = 'rgba(255,255,255,0.06)';
  ctx.fillRect(W / 2 - 1.5, 0, 3, H);

  // left: flying papers
  for (let i = 0; i < 7; i++) {
    ctx.save();
    ctx.translate(W / 4 + (hash(i) - 0.5) * 600 + Math.sin(L * 0.9 + i * 2) * 26, 120 + hash(i + 5) * 620 + Math.cos(L * 0.7 + i) * 22);
    ctx.rotate(hash(i + 3) * Math.PI + Math.sin(L + i) * 0.2);
    ctx.globalAlpha = 0.85;
    ctx.shadowColor = 'rgba(0,0,0,0.35)'; ctx.shadowBlur = 18; ctx.shadowOffsetY = 8;
    rr(ctx, -37, -48, 74, 96, 5);
    ctx.fillStyle = 'rgba(240,240,255,0.9)'; ctx.fill();
    ctx.shadowColor = 'transparent'; ctx.shadowBlur = 0; ctx.shadowOffsetY = 0;
    ctx.fillStyle = 'rgba(80,80,120,0.35)';
    rr(ctx, -27, -36, 54, 5, 2.5); ctx.fill();
    rr(ctx, -27, -26, 32, 5, 2.5); ctx.fill();
    rr(ctx, -27, -16, 40, 5, 2.5); ctx.fill();
    ctx.restore();
  }
  txt(ctx, 'ME · 12K PANIC', 44, 74, { size: 15, family: 'JBMB', color: '#ff8ac2', align: 'left' });

  // right: plants
  for (let i = 0; i < 6; i++) {
    const bx = W / 2 + 120 + i * 190;
    const by = 700 + hash(i + 11) * 120;
    const sway = Math.sin(L * 1.4 + i * 1.3) * 0.14;
    ctx.save();
    ctx.translate(bx, by);
    ctx.strokeStyle = '#2e7d5b'; ctx.lineWidth = 6; ctx.lineCap = 'round';
    ctx.beginPath(); ctx.moveTo(0, 0); ctx.quadraticCurveTo(sway * 60, -70, sway * 130, -150); ctx.stroke();
    for (let lf = 0; lf < 4; lf++) {
      const lp = 0.3 + lf * 0.22;
      const lx = sway * 130 * lp * lp;
      ctx.save();
      ctx.translate(lx, -150 * lp);
      ctx.rotate(sway * 2 + (lf % 2 ? 0.8 : -0.8));
      ctx.beginPath();
      ctx.moveTo(0, 0);
      ctx.quadraticCurveTo(38, -14, 58, 4);
      ctx.quadraticCurveTo(34, 18, 0, 6);
      ctx.closePath();
      ctx.fillStyle = lf % 2 ? '#43a37c' : '#2e7d5b';
      ctx.fill();
      ctx.restore();
    }
    ctx.fillStyle = '#b06a3c';
    rr(ctx, -30, -14, 60, 40, 6); ctx.fill();
    ctx.restore();
  }
  txt(ctx, 'MAYA · PLANTS & WISDOM', W - 44, 74, { size: 15, family: 'JBMB', color: '#7dffb0', align: 'right' });

  // bubbles
  const b1 = easeOutBack(beat(L, aPlants + 0.3, 0.4));
  if (b1 > 0) bubble(ctx, W - 250, 190, 520, '“If this is about your plants again — talking to them doesn\u2019t count as marketing.”', 'right', b1, 'rgba(190,255,220,0.96)', '#0d3b2e');
  const b2 = easeOutBack(beat(L, aTwelvek - 0.3, 0.4));
  if (b2 > 0) bubble(ctx, 270, 330, 520, '“Maya. I got a $12,000 order… going to an abandoned warehouse.”', 'left', b2, 'rgba(240,225,255,0.96)', '#2a1240');
  if (L > aDont - 1.4 && L < aDont + 0.6) {
    const p = beat(L, aDont - 1.4, 0.4);
    ctx.save();
    ctx.globalAlpha = p;
    ctx.fillStyle = 'rgba(255,255,255,0.5)';
    rr(ctx, W / 2 - 90, 436, 180, 36, 18); ctx.fill();
    txt(ctx, '…a beat…', W / 2, 460, { size: 15, family: 'JBMB', color: '#5c6a80' });
    ctx.restore();
  }
  const b3 = easeOutBack(beat(L, aDont - 0.5, 0.4));
  if (b3 > 0) bubble(ctx, W - 260, 500, 420, '“Okay. Do NOT ship that.”', 'right', b3, 'rgba(255,214,222,0.97)', '#7a0f2a');

  // comparison
  if (L > aVillain - 2.2) {
    const p = beat(L, aVillain - 2.2, 0.5);
    ctx.save();
    ctx.globalAlpha = p;
    const y = 610;
    ctx.fillStyle = 'rgba(230,255,240,0.95)';
    rr(ctx, W / 2 - 430, y - 26, 380, 52, 14); ctx.fill();
    txt(ctx, 'confirm like a normal human', W / 2 - 240, y + 6, { size: 19, family: 'SGB', color: '#0d5c3f' });
    txt(ctx, 'vs', W / 2, y + 8, { size: 26, family: 'AB', color: '#8f9bb3' });
    ctx.fillStyle = 'rgba(35,10,18,0.9)';
    rr(ctx, W / 2 + 50, y - 26, 380, 52, 14); ctx.fill();
    ctx.strokeStyle = '#ff4646'; ctx.lineWidth = 2;
    rr(ctx, W / 2 + 50, y - 26, 380, 52, 14); ctx.stroke();
    txt(ctx, 'like a movie villain', W / 2 + 240, y + 6, { size: 19, family: 'SGB', color: '#ff8fa3', rotate: -0.035 });
    ctx.restore();
  }

  // reactions floating
  if (L > aTwelvek) {
    const faces = ['D:', ':o', ':)', 'x_x'];
    faces.forEach((f, i) => {
      const p = ((L - aTwelvek) * 0.3 + i * 0.23) % 1;
      ctx.save();
      ctx.globalAlpha = (1 - p) * 0.9;
      ctx.translate(W / 2 - 120 + i * 80, 700 - p * 420);
      ctx.font = `700 38px SGB`;
      ctx.textAlign = 'center';
      ctx.fillStyle = '#fff';
      ctx.fillText(f, 0, 0);
      ctx.restore();
    });
  }

  // DO NOT SHIP stamp
  if (L > aDont + 0.4) {
    const p = beat(L, aDont + 0.4, 0.4);
    ctx.save();
    ctx.translate(W - 280, 300);
    ctx.rotate(-0.21);
    ctx.scale(0.6 + 0.4 * p, 0.6 + 0.4 * p);
    const pulse = 0.7 + 0.3 * Math.sin(L * 4.5);
    ctx.strokeStyle = `rgba(255,43,77,${pulse})`;
    ctx.lineWidth = 8;
    rr(ctx, -190, -44, 380, 88, 12); ctx.stroke();
    txt(ctx, 'DO NOT SHIP', 0, 14, { size: 52, family: 'AB', color: `rgba(255,43,77,${pulse})` });
    ctx.restore();
  }

  if (split > 0) {
    ctx.save();
    ctx.globalAlpha = split;
    ctx.fillStyle = '#05030c';
    ctx.fillRect(-300 * split, 0, W / 2 + 2, H);
    ctx.fillRect(W / 2 + 300 * split, 0, W / 2 + 2, H);
    ctx.restore();
  }
}

function bubble(ctx, x, y, w2, text, side, p, bg, color) {
  ctx.save();
  ctx.translate(x, y);
  const lines = wrapLines(ctx, text, { size: 22, family: 'SGB' }, w2 - 60);
  const h2 = lines.length * 32 + 40;
  ctx.scale(0.5 + 0.5 * p, 0.5 + 0.5 * p);
  ctx.globalAlpha = clamp01(p * 1.5);
  ctx.rotate(side === 'right' ? 0.012 : -0.02);
  ctx.shadowColor = 'rgba(0,0,0,0.4)'; ctx.shadowBlur = 26; ctx.shadowOffsetY = 12;
  rr(ctx, -w2 / 2, -h2 / 2, w2, h2, 18);
  ctx.fillStyle = bg; ctx.fill();
  ctx.shadowColor = 'transparent'; ctx.shadowBlur = 0; ctx.shadowOffsetY = 0;
  const tx = side === 'right' ? w2 / 2 - 34 : -w2 / 2 + 34;
  ctx.beginPath();
  ctx.moveTo(tx - 12, h2 / 2 - 2); ctx.lineTo(tx + 12, h2 / 2 - 2); ctx.lineTo(tx, h2 / 2 + 16);
  ctx.closePath();
  ctx.fillStyle = bg; ctx.fill();
  ctx.font = `700 22px SGB`;
  ctx.fillStyle = side === 'right' ? color : '#3a1440';
  ctx.textAlign = side === 'right' ? 'right' : 'left';
  const sx = side === 'right' ? w2 / 2 - 26 : -w2 / 2 + 26;
  lines.forEach((l, i) => ctx.fillText(l, sx, -h2 / 2 + 36 + i * 32));
  ctx.restore();
}

function wrapLines(ctx, text, o, maxW) {
  ctx.save();
  ctx.font = `${o.weight ?? 700} ${o.size}px ${o.family}`;
  const words = text.split(' ');
  const lines = [];
  let line = '';
  for (const w of words) {
    const test = line ? line + ' ' + w : w;
    if (ctx.measureText(test).width > maxW && line) {
      lines.push(line);
      line = w;
    } else line = test;
  }
  if (line) lines.push(line);
  ctx.restore();
  return lines;
}

// ---------------------------------------------------------------- SCENE 12
export function s12(ctx, L, t) {
  const end = 28.7;
  const narrow = clamp01((L - (end - 1.0)) / 1.0);
  const aDigging = A(12, 'digging');
  const aFirst = A(12, 'first');
  const aNothing = A(12, 'nothing');
  const aSecond = A(12, 'second');
  const aJetski = A(12, 'jetski');
  const aThird = A(12, 'third');
  const aLinked = A(12, 'linked');
  const aStomach = A(12, 'stomach');
  const aDoor = A(12, 'door');

  ctx.fillStyle = '#05060a'; ctx.fillRect(0, 0, W, H);

  // spotlights
  for (let i = 0; i < 3; i++) {
    ctx.save();
    ctx.translate(300 + i * 500, -40);
    ctx.rotate((i - 1) * 0.21 + Math.sin(L * 0.5 + i * 1.2) * 0.08);
    const sg = ctx.createLinearGradient(0, 0, 0, H * 1.2);
    sg.addColorStop(0, 'rgba(255,215,106,0.16)');
    sg.addColorStop(1, 'rgba(255,215,106,0)');
    ctx.fillStyle = sg;
    ctx.beginPath();
    ctx.moveTo(-30, 0); ctx.lineTo(30, 0); ctx.lineTo(170, H * 1.15); ctx.lineTo(-170, H * 1.15);
    ctx.closePath(); ctx.fill();
    ctx.restore();
  }

  txt(ctx, 'I decide to do a little digging', W / 2, 84, {
    size: 40, family: 'AB', color: '#ffd76a', glow: 'rgba(255,215,106,0.5)',
    alpha: beat(L, aDigging, 0.4),
  });

  const rows = [
    { n: 1, at: aFirst - 0.2, query: '9 rebar yard industrial edge of town' },
    { n: 2, at: aSecond - 0.2, query: '"elliot graye"' },
    { n: 3, at: aThird - 0.2, query: 'elliot.graye@very-real-buyer.com' },
  ];
  rows.forEach((r2, i) => {
    const p = easeOut(beat(L, r2.at, 0.4));
    if (p <= 0) return;
    const y = 150 + i * 148;
    ctx.save();
    ctx.globalAlpha = p;
    ctx.translate(0, (1 - p) * 30);
    panel(ctx, 260, y, 1080, 62, { r: 14, fill: 'rgba(10,12,18,0.85)', border: 'rgba(255,255,255,0.16)', shadow: false });
    txt(ctx, r2.n + '.', 296, y + 40, { size: 22, family: 'AB', color: '#ffd76a', align: 'left' });
    // magnifier
    ctx.strokeStyle = '#ffd76a'; ctx.lineWidth = 3.5;
    ctx.beginPath(); ctx.arc(348, y + 30, 12, 0, Math.PI * 2); ctx.stroke();
    ctx.beginPath(); ctx.moveTo(357, y + 39); ctx.lineTo(368, y + 50); ctx.stroke();
    const ty = typed(r2.query, r2.at + 0.2, 0.9, L);
    txt(ctx, ty.s, 392, y + 38, { size: 19, family: 'JBM', color: '#dfe6ff', align: 'left' });
    ctx.restore();

    if (i === 0 && L > aNothing) {
      const sp = easeOutBack(beat(L, aNothing, 0.3));
      ctx.save();
      ctx.translate(700, y + 118);
      ctx.rotate(-0.1);
      ctx.scale(sp, sp);
      ctx.strokeStyle = '#ff4646'; ctx.lineWidth = 4;
      rr(ctx, -160, -26, 320, 52, 8); ctx.stroke();
      txt(ctx, 'NOTHING FOUND', 0, 10, { size: 24, family: 'AB', color: '#ff4646' });
      ctx.restore();
    }
    if (i === 1 && L > aSecond + 0.6) {
      ['actor', 'dentist', 'jet-ski guy'].forEach((label, k) => {
        const cp = easeOutBack(beat(L, aSecond + 0.7 + k * 0.5, 0.4));
        if (cp <= 0) return;
        const cx = 480 + k * 230;
        ctx.save();
        ctx.translate(cx, y + 112);
        ctx.scale(0.8 + 0.2 * cp, 0.8 + 0.2 * cp);
        ctx.globalAlpha = cp;
        ctx.fillStyle = 'rgba(255,255,255,0.07)';
        rr(ctx, -88, -22, 176, 44, 12); ctx.fill();
        ctx.strokeStyle = 'rgba(255,255,255,0.16)'; ctx.lineWidth = 1.5;
        rr(ctx, -88, -22, 176, 44, 12); ctx.stroke();
        txt(ctx, label, 0, 7, { size: 18, family: 'SGB', color: '#dfe6ff' });
        if (L > aJetski + 0.3 + k * 0.12) {
          ctx.strokeStyle = '#ff4646'; ctx.lineWidth = 6; ctx.lineCap = 'round';
          ctx.beginPath(); ctx.moveTo(-60, -14); ctx.lineTo(60, 14); ctx.stroke();
          ctx.beginPath(); ctx.moveTo(60, -14); ctx.lineTo(-60, 14); ctx.stroke();
        }
        ctx.restore();
      });
    }
    if (i === 2 && L > aLinked) {
      const p = beat(L, aLinked, 0.3);
      ctx.save();
      ctx.globalAlpha = p;
      ctx.translate(560 + (hash(Math.floor(L * 14)) - 0.5) * 5, y + 112);
      txt(ctx, 'linked to…', 0, 0, { size: 19, family: 'JBMB', color: '#ff8fa3', align: 'left' });
      txt(ctx, 'NOTHING.', 130, 0, { size: 24, family: 'AB', color: '#fff', align: 'left', glow: 'rgba(255,70,70,0.6)' });
      ctx.restore();
    }
  });

  // stomach drop
  if (L > aStomach) {
    const drop = clamp01((L - aStomach) / 1.4);
    ctx.save();
    ctx.globalAlpha = clamp01(1.4 - drop);
    ctx.translate(W / 2, 60 + drop * 640);
    ctx.scale(1 - drop * 0.2, 1 - drop * 0.2);
    txt(ctx, 'my stomach drops', 3, 3, { size: 74, family: 'AB', color: 'rgba(255,70,70,0.3)' });
    txt(ctx, 'my stomach drops', 0, 0, { size: 74, family: 'AB', color: '#ff5c5c', glow: 'rgba(255,70,70,0.45)' });
    ctx.restore();
  }

  // door line flicker
  if (L > aDoor - 0.4) {
    ctx.save();
    ctx.globalAlpha = Math.sin(L * 22) > -0.2 ? 1 : 0.15;
    // little door
    const dx = W / 2 - 420;
    ctx.fillStyle = 'rgba(255,255,255,0.08)';
    rr(ctx, dx - 30, 640, 60, 96, 6); ctx.fill();
    ctx.strokeStyle = 'rgba(255,255,255,0.4)'; ctx.lineWidth = 2;
    rr(ctx, dx - 30, 640, 60, 96, 6); ctx.stroke();
    ctx.fillStyle = '#fff';
    ctx.beginPath(); ctx.arc(dx + 14, 692, 4, 0, Math.PI * 2); ctx.fill();
    txt(ctx, '“Don\u2019t open the door.”', W / 2 + 80, 700, {
      size: 44, family: 'AB', color: '#fff', glow: 'rgba(255,70,70,0.8)',
    });
    ctx.restore();
  }

  if (narrow > 0) {
    ctx.save();
    ctx.globalAlpha = narrow;
    ctx.fillStyle = '#05060a';
    ctx.beginPath();
    ctx.rect(0, 0, W, H);
    ctx.arc(W / 2, H * 0.46, H * 0.6 * (1 - narrow * 0.5), 0, Math.PI * 2, true);
    ctx.fill();
    ctx.restore();
  }
}

// ---------------------------------------------------------------- SCENE 13
export function s13(ctx, L, t) {
  const end = 34.3;
  const crack = clamp01((L - (end - 1.0)) / 1.0);
  const aAnother = A(13, 'another');
  const aNoTrack = A(13, 'notracking');
  const aFourteen = A(13, 'fourteen');
  const aPolite = A(13, 'polite');
  const aNoTime = A(13, 'notime');
  const aCold = A(13, 'cold');
  const aCountdown = A(13, 'countdown');

  // red ambient pulse
  const pulse = 0.5 + 0.5 * Math.sin(L * 4);
  const g = ctx.createRadialGradient(W / 2, H * 0.4, 0, W / 2, H * 0.4, 700);
  g.addColorStop(0, `rgba(255,59,92,${0.08 + 0.06 * pulse})`);
  g.addColorStop(1, 'rgba(255,59,92,0)');
  ctx.fillStyle = g; ctx.fillRect(0, 0, W, H);

  txt(ctx, 'then I get another email', W / 2, 80, {
    size: 40, family: 'AB', color: '#ff5c7a', glow: 'rgba(255,59,92,0.6)',
    alpha: beat(L, aAnother, 0.4),
  });

  // timer
  if (L > aFourteen - 0.5) {
    const p = easeOutBack(beat(L, aFourteen - 0.5, 0.5));
    ctx.save();
    ctx.translate(1310, 240);
    ctx.scale(p, p);
    panel(ctx, -170, -95, 340, 190, { r: 20, fill: 'rgba(20,2,8,0.75)', border: 'rgba(255,59,92,0.5)' });
    txt(ctx, 'SINCE ORDER', 0, -50, { size: 13, family: 'JBMB', color: '#ff8fa3' });
    const mins = Math.max(0, 14 - Math.max(0, L - aFourteen) * 2.4 / 60 * 60 / 60);
    const tot = Math.max(0, 14 * 60 - Math.max(0, L - aFourteen) * 144);
    const mm = Math.floor(tot / 60);
    const ss = Math.floor(tot % 60);
    txt(ctx, `${String(mm).padStart(2, '0')}:${String(ss).padStart(2, '0')}`, 0, 18, {
      size: 64, family: 'JBMB', color: '#ff4646', glow: 'rgba(255,70,70,0.6)',
    });
    txt(ctx, 'and counting', 0, 66, { size: 13, family: 'JBM', color: '#ff8fa3' });
    ctx.restore();
  }

  // thread
  const e1 = easeOut(beat(L, aNoTrack - 0.5, 0.5));
  if (e1 > 0) {
    ctx.save();
    ctx.globalAlpha = e1;
    ctx.translate(lerp(-320, 0, e1), 0);
    panel(ctx, 150, 170, 720, 104, { r: 16, fill: 'rgba(26,4,10,0.75)', border: 'rgba(255,59,92,0.5)', shadow: false });
    txt(ctx, 'from: elliot graye · 2:26 AM', 180, 200, { size: 13, family: 'JBM', color: '#ff9db1', align: 'left' });
    const pw = 1 + 0.04 * Math.sin(L * 5.5);
    ctx.save();
    ctx.translate(180, 240); ctx.scale(pw, pw);
    txt(ctx, '“Why no tracking yet?”', 0, 0, { size: 27, family: 'AB', color: '#ffdde3', align: 'left', glow: 'rgba(255,70,70,0.5)' });
    ctx.restore();
    ctx.restore();
  }

  const e2 = easeOut(beat(L, aPolite - 0.3, 0.5));
  if (e2 > 0) {
    ctx.save();
    ctx.globalAlpha = e2;
    ctx.translate(lerp(320, 0, e2), 0);
    panel(ctx, 240, 296, 830, 130, { r: 16, fill: 'rgba(6,12,22,0.75)', border: 'rgba(97,176,255,0.4)', shadow: false });
    txt(ctx, 'to: elliot graye · drafting calmly…', 270, 328, { size: 13, family: 'JBM', color: '#7dd8a8', align: 'left' });
    const ty = typed('“Hi! For high-volume orders, we confirm shipping details for security…”', aPolite + 0.3, 1.8, L);
    ctx.font = `400 18.5px JBM`; ctx.fillStyle = '#cfe4ff'; ctx.textAlign = 'left';
    wrapText2(ctx, ty.s, 270, 360, 760, 27);
    ctx.restore();
  }

  if (L > aNoTime - 0.6) {
    const p = beat(L, aNoTime - 0.6, 0.3);
    const wob = L < aNoTime + 1.2 && L > aNoTime - 0.4;
    ctx.save();
    ctx.globalAlpha = p;
    ctx.translate(450 + (wob ? (hash(Math.floor(L * 90)) - 0.5) * 12 : 0), 490 + (wob ? (hash(Math.floor(L * 90) + 9) - 0.5) * 12 : 0));
    ctx.scale(0.6 + 0.4 * p, 0.6 + 0.4 * p);
    panel(ctx, -330, -56, 760, 112, { r: 16, fill: 'rgba(48,0,10,0.85)', border: '#ff4646', glow: 'rgba(255,70,70,0.4)' });
    txt(ctx, 'from: elliot graye · INSTANT', -300, -22, { size: 13, family: 'JBM', color: '#ff9db1', align: 'left' });
    txt(ctx, '“No time. Ship now.', -300, 18, { size: 30, family: 'AB', color: '#fff', align: 'left', glow: 'rgba(255,70,70,0.8)' });
    const pp = 0.75 + 0.25 * Math.sin(L * 8);
    txt(ctx, 'I paid.”', -300 + measure(ctx, '“No time. Ship now.', { size: 30, family: 'AB' }) + 14, 18, {
      size: 30, family: 'AB', color: `rgba(255,70,70,${pp})`, align: 'left',
    });
    ctx.restore();
  }

  if (L > aCold - 0.4) {
    const p = beat(L, aCold - 0.4, 0.4);
    ctx.save();
    ctx.globalAlpha = p;
    txt(ctx, 'now my hands are cold', W / 2, 640, { size: 40, family: 'CVB', color: '#bfe4ff' });
    if (L > aCountdown - 0.2) {
      const p2 = beat(L, aCountdown - 0.2, 0.4);
      ctx.globalAlpha = p2;
      const word = "THAT'S NOT A CUSTOMER. THAT'S A";
      const w2 = measure(ctx, word, { size: 34, family: 'AB' });
      const w3 = measure(ctx, 'COUNTDOWN.', { size: 46, family: 'AB' });
      txt(ctx, word, W / 2 - (w3 + 20) / 2, 706, { size: 34, family: 'AB', color: '#fff', align: 'right' });
      txt(ctx, 'COUNTDOWN.', W / 2 + (w2 + 20) / 2, 706, {
        size: 46, family: 'AB', color: '#61b0ff', glow: 'rgba(97,176,255,0.8)', align: 'left',
        alpha: 0.75 + 0.25 * Math.sin(L * 7),
      });
    }
    ctx.restore();
  }

  // icy edges
  if (L > aCold) {
    const a2 = 0.35 + 0.15 * Math.sin(L * 2);
    ctx.save();
    ctx.strokeStyle = `rgba(190,230,255,${a2})`;
    ctx.lineWidth = 46;
    ctx.strokeRect(-10, -10, W + 20, H + 20);
    ctx.strokeStyle = `rgba(190,230,255,${a2 * 0.5})`;
    ctx.lineWidth = 90;
    ctx.strokeRect(-30, -30, W + 60, H + 60);
    ctx.restore();
  }

  // glass crack
  if (crack > 0) {
    const cracks = [
      [800, 450, 500, 180, 420, 60], [800, 450, 1150, 220, 1260, 80],
      [800, 450, 460, 700, 340, 850], [800, 450, 1120, 680, 1240, 860],
      [800, 450, 800, 40], [800, 450, 250, 420, 60, 380], [800, 450, 1360, 470, 1560, 520],
    ];
    ctx.save();
    ctx.strokeStyle = 'rgba(255,255,255,0.85)';
    ctx.lineWidth = 2.4;
    ctx.shadowColor = 'rgba(255,255,255,0.6)'; ctx.shadowBlur = 6;
    cracks.forEach((c, i) => {
      const prog = clamp01(crack * 1.6 - i * 0.08);
      if (prog <= 0) return;
      ctx.beginPath();
      ctx.moveTo(c[0], c[1]);
      const segs = 8;
      for (let s2 = 1; s2 <= segs * prog; s2++) {
        const p = s2 / segs;
        const last = s2 === segs;
        const tx = last ? c[c.length - 2] : lerp(c[0], c[c.length - 2], p) + (hash(i * 31 + s2) - 0.5) * 40;
        const ty = last ? c[c.length - 1] : lerp(c[1], c[c.length - 1], p) + (hash(i * 17 + s2) - 0.5) * 40;
        ctx.lineTo(lerp(c[0], tx, p), lerp(c[1], ty, p));
      }
      ctx.stroke();
    });
    ctx.restore();
  }
}

function wrapText2(ctx, text, x, y, maxW, lh) {
  const words = text.split(' ');
  let line = '';
  let yy = y;
  for (const w of words) {
    const test = line ? line + ' ' + w : w;
    if (ctx.measureText(test).width > maxW && line) {
      ctx.fillText(line, x, yy);
      line = w;
      yy += lh;
    } else line = test;
  }
  if (line) ctx.fillText(line, x, yy);
}

// ---------------------------------------------------------------- SCENE 14
export function s14(ctx, L, t) {
  const end = 53.1;
  const fade = clamp01((L - (end - 1.1)) / 1.1);
  const aStand = A(14, 'stand');
  const aSerenade = A(14, 'serenade');
  const aRep = A(14, 'rep');
  const aHighRisk = A(14, 'highrisk');
  const aScam = A(14, 'scam');

  const winPop = easeOutBack(beat(L, aStand, 0.5));
  if (winPop > 0) {
    ctx.save();
    ctx.translate(W / 2, 320);
    ctx.scale(winPop, winPop);
    panel(ctx, -320, -210, 640, 430, { r: 24, fill: 'rgba(6,14,26,0.9)', border: 'rgba(97,176,255,0.35)', shadowBlur: 70 });
    // avatar + waves
    ctx.beginPath(); ctx.arc(0, -108, 56, 0, Math.PI * 2);
    const ag = ctx.createLinearGradient(-56, -164, 56, -52);
    ag.addColorStop(0, '#61b0ff'); ag.addColorStop(1, '#7a5cff');
    ctx.fillStyle = ag; ctx.fill();
    // headset
    ctx.strokeStyle = '#0a1626'; ctx.lineWidth = 7; ctx.lineCap = 'round';
    ctx.beginPath(); ctx.arc(0, -116, 38, Math.PI * 1.15, Math.PI * 1.85); ctx.stroke();
    ctx.beginPath(); ctx.arc(-36, -104, 10, 0, Math.PI * 2); ctx.fillStyle = '#0a1626'; ctx.fill();
    ctx.beginPath(); ctx.arc(36, -104, 10, 0, Math.PI * 2); ctx.fill();
    for (let i = 0; i < 2; i++) {
      const rp = ((L * 0.7 + i * 0.5) % 1);
      ctx.beginPath(); ctx.arc(0, -108, 58 + rp * 46, 0, Math.PI * 2);
      ctx.strokeStyle = `rgba(97,176,255,${0.5 * (1 - rp)})`;
      ctx.lineWidth = 3;
      ctx.stroke();
    }
    txt(ctx, 'PAYMENT PROCESSOR SUPPORT', 0, -8, { size: 27, family: 'AB', color: '#dfeaff' });
    const callSecs = Math.max(0, L - (aSerenade - 1.2));
    const mm = Math.floor(callSecs / 60);
    const ss = Math.floor(callSecs % 60);
    txt(ctx, `${String(mm).padStart(2, '0')}:${String(ss).padStart(2, '0')} · on hold`, 0, 34, {
      size: 20, family: 'JBM', color: '#8fd3ff',
    });
    // sad equalizer
    for (let i = 0; i < 12; i++) {
      const droop = Math.abs(Math.sin(L * 1.1 + i * 0.7));
      const h2 = 12 + droop * 66;
      const bx = -218 + i * 36;
      ctx.save();
      ctx.translate(bx, 120);
      ctx.rotate((hash(i) - 0.5) * 0.16);
      const bg2 = ctx.createLinearGradient(0, -h2, 0, 0);
      bg2.addColorStop(0, '#61b0ff'); bg2.addColorStop(1, '#2b4a8f');
      ctx.fillStyle = bg2;
      ctx.globalAlpha = 0.75;
      rr(ctx, -8, -h2, 16, h2, 6); ctx.fill();
      ctx.restore();
    }
    // sad notes (upside down)
    note(ctx, -80, 158 + Math.sin(L * 1.4) * 8, 26, 'rgba(143,211,255,0.75)', 0.75);
    note(ctx, 0, 176 + Math.sin(L * 1.2 + 2) * 8, 30, 'rgba(143,211,255,0.6)', 0.6);
    note(ctx, 86, 162 + Math.sin(L * 1.6 + 4) * 8, 24, 'rgba(143,211,255,0.75)', 0.75);
    ctx.restore();
  }

  // rep card
  if (L > aRep - 0.4) {
    const p = easeOutBack(beat(L, aRep - 0.4, 0.5));
    ctx.save();
    ctx.globalAlpha = p;
    ctx.translate(lerp(-60, 130, easeOut(p)), 0);
    panel(ctx, 130, 620, 470, 110, { r: 16, fill: 'rgba(8,20,14,0.85)', border: 'rgba(125,216,168,0.4)' });
    ctx.beginPath(); ctx.arc(190, 668, 26, 0, Math.PI * 2);
    ctx.fillStyle = '#2e7d5b'; ctx.fill();
    txt(ctx, 'REP', 190, 675, { size: 15, family: 'AB', color: '#d9ffe9' });
    txt(ctx, 'Support Rep', 240, 656, { size: 20, family: 'SGB', color: '#d9ffe9', align: 'left' });
    txt(ctx, '“I can\u2019t confirm details… but…”', 240, 688, { size: 14, family: 'JBM', color: '#7dd8a8', align: 'left' });
    ctx.restore();
  }

  // HIGH RISK badge + gauge
  if (L > aHighRisk - 0.5) {
    const p = beat(L, aHighRisk - 0.5, 0.4);
    ctx.save();
    ctx.globalAlpha = p;
    ctx.translate(1330, 220);
    ctx.rotate(0.1);
    const pulse = 0.7 + 0.3 * Math.sin(L * 5.5);
    ctx.strokeStyle = `rgba(255,211,92,${pulse})`;
    ctx.lineWidth = 6;
    rr(ctx, -150, -42, 300, 84, 14); ctx.stroke();
    txt(ctx, 'HIGH RISK', 0, 14, { size: 44, family: 'AB', color: `rgba(255,211,92,${pulse})`, glow: 'rgba(255,211,92,0.4)' });
    ctx.restore();
    // gauge
    ctx.save();
    ctx.translate(1330, 300);
    rr(ctx, -17, 0, 34, 190, 18);
    ctx.fillStyle = 'rgba(255,255,255,0.06)'; ctx.fill();
    ctx.strokeStyle = 'rgba(255,255,255,0.25)'; ctx.lineWidth = 3; ctx.stroke();
    const fill = clamp01((L - aHighRisk + 0.5) / 3) * 190;
    if (fill > 0) {
      ctx.save();
      rr(ctx, -17, 0, 34, 190, 18); ctx.clip();
      const gg = ctx.createLinearGradient(0, 190, 0, 0);
      gg.addColorStop(0, '#7dd8a8'); gg.addColorStop(0.5, '#ffd35c'); gg.addColorStop(1, '#ff4646');
      ctx.fillStyle = gg;
      ctx.fillRect(-17, 190 - fill, 34, fill);
      ctx.restore();
    }
    txt(ctx, 'TEMPERATURE', 0, 216, { size: 12.5, family: 'JBMB', color: '#ffb3b3' });
    ctx.restore();
  }

  // sinking "So… scam."
  if (L > aScam - 0.4) {
    const sink = clamp01((L - aScam + 0.4) / 2);
    ctx.save();
    ctx.globalAlpha = clamp01((L - aScam + 0.4) * 2) * (1 - fade);
    ctx.translate(W / 2, 560 + sink * 26);
    txt(ctx, '“So… scam.”', 0, 0, { size: 64, family: 'AB', color: '#ff5c5c', glow: 'rgba(255,70,70,0.4)' });
    ctx.restore();
  }

  txt(ctx, 'I call the payment processor', W / 2, 76, {
    size: 36, family: 'AB', color: '#9fc6ff', alpha: beat(L, aStand, 0.4),
  });

  if (fade > 0) {
    ctx.fillStyle = `rgba(0,0,0,${fade})`;
    ctx.fillRect(0, 0, W, H);
  }
}

// ---------------------------------------------------------------- SCENE 15
export function s15(ctx, L, t) {
  const aAnother = A(15, 'another');
  const aOneHour = A(15, 'onehour');
  const aClicks = A(15, 'clicks');
  const aPressure = A(15, 'pressure');
  const aYouWill = A(15, 'youwillship');
  const aLaughFear = A(15, 'laughfear');

  // subtle frame jitter
  ctx.save();
  ctx.translate((hash(Math.floor(t * 12)) - 0.5) * 3, (hash(Math.floor(t * 12) + 7) - 0.5) * 3);

  if (L > aAnother - 0.3) {
    const p = beat(L, aAnother - 0.3, 0.35);
    ctx.save();
    ctx.translate(W / 2, 62);
    ctx.scale(0.6 + 0.4 * p, 0.6 + 0.4 * p);
    const pulse = 0.75 + 0.25 * Math.sin(L * 6.5);
    ctx.fillStyle = `rgba(255,70,70,${pulse})`;
    rr(ctx, -170, -26, 340, 52, 12); ctx.fill();
    txt(ctx, 'NEW EMAIL · 2:41 AM', 0, 8, { size: 20, family: 'AB', color: '#fff' });
    ctx.restore();
  }

  if (L > aOneHour - 0.3) {
    const p = easeOut(beat(L, aOneHour - 0.3, 0.5));
    ctx.save();
    ctx.globalAlpha = p;
    ctx.translate(W / 2, 208);
    ctx.rotate(-0.02);
    panel(ctx, -440, -66, 880, 132, { r: 16, fill: 'rgba(24,2,6,0.85)', border: 'rgba(255,70,70,0.6)' });
    txt(ctx, 'FROM: ELLIOT · SUBJECT: (no subject)', -400, -30, { size: 13, family: 'JBMB', color: '#ff9db1', align: 'left' });
    txt(ctx, '“IF YOU DON\u2019T SHIP IN 1 HOUR I WILL', -400, 10, { size: 26, family: 'AB', color: '#ffdde3', align: 'left' });
    txt(ctx, 'REPORT YOU. REFUND ME NOW.”', -400, 46, { size: 26, family: 'AB', color: '#ff4646', align: 'left' });
    ctx.restore();
  }

  // puzzle + lightbulb
  if (L > aClicks - 1.4) {
    const cols = ['#ffd35c', '#7dd8a8', '#9fc6ff', '#ff8ac2'];
    cols.forEach((c, i) => {
      const p = easeOutBack(beat(L, aClicks - 1.2 + i * 0.28, 0.35));
      if (p <= 0) return;
      ctx.save();
      ctx.translate(1330 + (i % 2) * 70, 330 + Math.floor(i / 2) * 70);
      ctx.rotate((1 - p) * 1.5);
      ctx.scale(p, p);
      ctx.fillStyle = c;
      rr(ctx, -30, -30, 60, 60, 8); ctx.fill();
      ctx.fillStyle = 'rgba(0,0,0,0.25)';
      ctx.beginPath(); ctx.arc(0, -30, 10, 0, Math.PI * 2); ctx.fill();
      ctx.restore();
    });
    if (L > aClicks - 1.3) {
      const p = beat(L, aClicks - 1.3, 0.3);
      const pulse = 0.8 + 0.2 * Math.sin(L * 5);
      ctx.save();
      ctx.globalAlpha = p * pulse;
      ctx.translate(1365, 530);
      // rays
      ctx.strokeStyle = '#ffd35c'; ctx.lineWidth = 4; ctx.lineCap = 'round';
      for (let i = 0; i < 8; i++) {
        const a = (i / 8) * Math.PI * 2 + L;
        ctx.beginPath();
        ctx.moveTo(Math.cos(a) * 46, Math.sin(a) * 46 + 6);
        ctx.lineTo(Math.cos(a) * 60, Math.sin(a) * 60 + 6);
        ctx.stroke();
      }
      ctx.beginPath(); ctx.arc(0, 0, 30, 0, Math.PI * 2);
      ctx.fillStyle = '#ffd35c';
      ctx.shadowColor = 'rgba(255,211,92,0.9)'; ctx.shadowBlur = 44;
      ctx.fill();
      ctx.shadowColor = 'transparent';
      rr(ctx, -12, 32, 24, 20, 4); ctx.fill();
      ctx.restore();
    }
  }

  // scheme card
  if (L > aPressure - 0.4) {
    const p = easeOut(beat(L, aPressure - 0.4, 0.5));
    ctx.save();
    ctx.globalAlpha = p;
    ctx.translate(lerp(-60, 130, easeOut(p)), 0);
    panel(ctx, 130, 300, 480, 260, { r: 20, fill: 'rgba(10,4,10,0.88)', border: 'rgba(255,70,70,0.3)' });
    txt(ctx, 'THE PRESSURE PLAYBOOK', 160, 340, { size: 13, family: 'JBMB', color: '#ff9db1', align: 'left' });
    const schemes = [['panic → hit “refund”', '#ff4646'], ['money rerouted elsewhere', '#ff9a3c'], ['shipment proof → dispute win', '#ffd35c']];
    schemes.forEach((s2, i) => {
      const sp = beat(L, aPressure + i * 0.7, 0.45);
      if (sp <= 0) return;
      ctx.save();
      ctx.globalAlpha = sp;
      ctx.translate(lerp(-26, 0, sp), 0);
      txt(ctx, '▼', 168, 382 + i * 40, { size: 20, family: 'SGB', color: s2[1], align: 'left' });
      txt(ctx, s2[0], 200, 382 + i * 40, { size: 20, family: 'SGB', color: '#ffe8ec', align: 'left' });
      ctx.restore();
    });
    txt(ctx, '“this isn\u2019t about planners…', 160, 512, { size: 27, family: 'CVB', color: '#ffd6e0', align: 'left' });
    txt(ctx, 'it\u2019s about pressure.”', 160, 544, { size: 27, family: 'CVB', color: '#ffd6e0', align: 'left' });
    ctx.restore();
  }

  // RANSOM NOTE
  if (L > aYouWill - 0.5) {
    const lines = ['YOU WILL SHIP.', 'I KNOW WHERE YOU LIVE.'];
    const colors = ['#ff4646', '#ffd35c', '#7dd8a8', '#9fc6ff', '#ff8ac2', '#ffffff'];
    lines.forEach((line, li) => {
      ctx.save();
      ctx.translate(W / 2, 610 + li * 84);
      let totalW = 0;
      const widths = line.split('').map((ch, i) => {
        const h1 = hash(i + li * 31);
        const fam = h1 > 0.66 ? 'AB' : h1 > 0.33 ? 'JBMB' : 'CVB';
        const w2 = measure(ctx, ch, { size: 52 + h1 * 26, family: fam }) + 5;
        totalW += w2;
        return { w: w2, fam, h1 };
      });
      let x = -totalW / 2;
      line.split('').forEach((ch, i) => {
        const { w: w2, fam, h1 } = widths[i];
        const p = beat(L, aYouWill - 0.4 + li * 0.5 + i * 0.032, 0.3);
        if (p > 0) {
          ctx.save();
          ctx.globalAlpha = p;
          ctx.translate(x + w2 / 2, (1 - p) * -70);
          ctx.rotate((h1 - 0.5) * 0.45);
          if (h1 > 0.5) {
            ctx.fillStyle = 'rgba(255,255,255,0.92)';
            rr(ctx, -w2 / 2 + 2, -34, w2 - 4, 56, 3); ctx.fill();
          }
          txt(ctx, ch, 0, 18, {
            size: 44 + h1 * 30, family: fam, color: colors[(i + li) % colors.length],
          });
          ctx.restore();
        }
        x += w2;
      });
      ctx.restore();
    });
  }

  if (L > aLaughFear - 0.5) {
    txt(ctx, 'I laugh… but it\u2019s fear wearing a comedy mask', W / 2, 500, {
      size: 30, family: 'CVB', color: '#ffd6e0', alpha: beat(L, aLaughFear - 0.5, 0.4),
    });
  }

  // shield
  if (L > aLaughFear + 0.6) {
    const p = easeOutBack(beat(L, aLaughFear + 0.6, 0.6));
    ctx.save();
    ctx.translate(1340, 700);
    ctx.scale(p, p);
    ctx.rotate(-0.1 + Math.sin(L * 2) * 0.07);
    ctx.shadowColor = 'rgba(125,216,168,0.8)'; ctx.shadowBlur = 50;
    ctx.beginPath();
    ctx.moveTo(-52, -60); ctx.lineTo(52, -60); ctx.lineTo(52, 20);
    ctx.quadraticCurveTo(52, 62, 0, 84); ctx.quadraticCurveTo(-52, 62, -52, 20);
    ctx.closePath();
    ctx.fillStyle = 'rgba(125,216,168,0.28)'; ctx.fill();
    ctx.shadowColor = 'transparent';
    ctx.strokeStyle = '#7dd8a8'; ctx.lineWidth = 6; ctx.stroke();
    ctx.strokeStyle = '#eafff5'; ctx.lineWidth = 7; ctx.lineCap = 'round';
    ctx.beginPath(); ctx.moveTo(-20, -6); ctx.lineTo(-4, 14); ctx.lineTo(26, -26); ctx.stroke();
    ctx.restore();
  }
  ctx.restore();
}

// ---------------------------------------------------------------- SCENE 16
export function s16(ctx, L, t) {
  const end = 79.7;
  const white = clamp01((L - (end - 1.2)) / 1.2);
  const aScreenshot = A(16, 'screenshot');
  const aCancelled = A(16, 'cancelled');
  const aSpikes = A(16, 'spikes');
  const aVending = A(16, 'vending');
  const aBootcamp = A(16, 'bootcamp');
  const aDrops = A(16, 'drops');
  const aSilence = A(16, 'silence');
  const green = beat(L, aDrops, 0.8);

  // tech grid
  ctx.save();
  ctx.strokeStyle = 'rgba(0,194,255,0.10)';
  ctx.lineWidth = 1.5;
  const off = (L * 24) % 70;
  for (let x = -70 + off; x < W + 70; x += 70) { ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x, H); ctx.stroke(); }
  for (let y = -70 + off; y < H + 70; y += 70) { ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(W, y); ctx.stroke(); }
  ctx.restore();

  // screenshot flash
  if (L > aScreenshot - 0.3 && L < aScreenshot + 1.2) {
    const a2 = (1 - beat(L, aScreenshot - 0.3, 0.3)) * 0.9;
    ctx.fillStyle = `rgba(255,255,255,${a2})`;
    ctx.fillRect(0, 0, W, H);
  }

  // cancelled banner
  if (L > aCancelled - 0.6) {
    const p = easeOutBack(beat(L, aCancelled - 0.6, 0.5));
    ctx.save();
    ctx.translate(W / 2, 138);
    ctx.scale(p, p);
    panel(ctx, -430, -52, 860, 104, { r: 18, fill: 'rgba(3,18,12,0.8)', border: 'rgba(0,255,136,0.5)', glow: 'rgba(0,255,136,0.25)' });
    txt(ctx, 'ORDER #1043', 0, -18, { size: 13, family: 'JBMB', color: '#7dd8a8' });
    txt(ctx, 'CANCELLED · FUNDS REVERSED · NO SHIPMENT', 0, 22, { size: 30, family: 'AB', color: '#00ff88', glow: 'rgba(0,255,136,0.5)' });
    ctx.restore();
  }

  // traffic chart
  if (L > aSpikes - 0.5) {
    const p = easeOut(beat(L, aSpikes - 0.5, 0.5));
    ctx.save();
    ctx.globalAlpha = p;
    ctx.translate(lerp(-60, 120, easeOut(p)), 0);
    panel(ctx, 120, 300, 560, 300, { r: 20, fill: 'rgba(2,8,16,0.85)', border: 'rgba(0,194,255,0.3)' });
    txt(ctx, 'CHECKOUT TRAFFIC · LIVE', 150, 340, { size: 13, family: 'JBMB', color: '#9fc6ff', align: 'left' });
    const cp = easeOut(beat(L, aSpikes + 0.2, 2));
    const hits = Math.round(847 * cp);
    txt(ctx, hits + ' hits', 640, 344, { size: 24, family: 'JBMB', color: green > 0.5 ? '#00ff88' : '#ff4646', align: 'right' });
    for (let i = 0; i < 26; i++) {
      const tt = i / 26;
      let spike = tt < 0.55 ? 0.25 + hash(i) * 0.55 + tt * 0.9 : Math.max(0.06, 1 - (tt - 0.55) / 0.45) * (0.3 + hash(i) * 0.4);
      spike *= green > 0 ? 1 - green * 0.85 : 1;
      const h2 = 10 + spike * 150;
      const appear = beat(L, aSpikes + 0.2 + i * 0.05, 0.3);
      if (appear <= 0) continue;
      const col = green > 0.5 ? '#00ff88' : '#ff4646';
      ctx.save();
      ctx.globalAlpha *= appear;
      const bg2 = ctx.createLinearGradient(0, 560 - h2, 0, 560);
      bg2.addColorStop(0, col); bg2.addColorStop(1, rgba(col, 0.33));
      ctx.fillStyle = bg2;
      rr(ctx, 152 + i * 19.4, 560 - h2, 13, h2, 4); ctx.fill();
      ctx.restore();
    }
    ctx.fillStyle = green > 0.5 ? '#7dd8a8' : '#ff8fa3';
    ctx.font = `700 12.5px JBM`; ctx.textAlign = 'left';
    ctx.fillText(green > 0.5 ? 'traffic dropping… silence returns' : 'bot barrage · testing cards · different names', 150, 584);
    ctx.restore();
  }

  // vending machine
  if (L > aVending - 0.3) {
    const p = beat(L, aVending - 0.3, 0.4);
    ctx.save();
    ctx.globalAlpha = p;
    ctx.translate(1330, 420);
    ctx.rotate(0.035);
    panel(ctx, -215, -110, 430, 240, { r: 18, fill: 'rgba(20,4,10,0.78)', border: 'rgba(255,70,70,0.4)' });
    // machine
    ctx.fillStyle = '#ff4646';
    rr(ctx, -60, -86, 120, 160, 10); ctx.fill();
    ctx.fillStyle = 'rgba(255,255,255,0.25)';
    rr(ctx, -48, -74, 66, 90, 5); ctx.fill();
    ctx.fillStyle = 'rgba(0,0,0,0.35)';
    rr(ctx, 26, -40, 22, 32, 3); ctx.fill();
    for (let i = 0; i < 6; i++) {
      ctx.fillStyle = ['#ffd35c', '#7dd8a8', '#9fc6ff'][i % 3];
      rr(ctx, -44 + (i % 3) * 20, -70 + Math.floor(i / 3) * 26, 14, 20, 2); ctx.fill();
    }
    txt(ctx, '“Oh my god, I\u2019m a vending', 0, 106, { size: 22, family: 'AB', color: '#ff8fa3' });
    txt(ctx, 'machine to them.”', 0, 134, { size: 22, family: 'AB', color: '#ff8fa3' });
    ctx.restore();
  }

  // bootcamp line
  if (L > aBootcamp - 0.4) {
    txt(ctx, 'the fastest entrepreneur bootcamp — 20 minutes', W / 2, 250, {
      size: 34, family: 'AB', color: '#9fe8ff', glow: 'rgba(0,194,255,0.5)',
      alpha: beat(L, aBootcamp - 0.4, 0.4),
    });
  }

  // checklist
  if (L > aBootcamp + 0.5) {
    const p = easeOut(beat(L, aBootcamp + 0.5, 0.5));
    ctx.save();
    ctx.globalAlpha = p;
    ctx.translate(lerp(60, -130, easeOut(p)), 0);
    panel(ctx, 960, 470, 510, 330, { r: 20, fill: 'rgba(2,10,18,0.88)', border: 'rgba(0,194,255,0.35)' });
    txt(ctx, 'LOCKDOWN CHECKLIST', 990, 508, { size: 13, family: 'JBMB', color: '#9fc6ff', align: 'left' });
    const checks = [
      ['filters', 'stricter fraud filters'],
      ['regions', 'block certain regions'],
      ['verify', 'address verification'],
      ['bulk', 'disable bulk quantities'],
      ['captcha', 'captcha on checkout'],
      ['breathe', 'breathe'],
    ];
    checks.forEach(([key, label], i) => {
      const at = A(16, key) - 0.15;
      const on = beat(L, at, 0.4);
      const y = 544 + i * 40;
      // toggle
      ctx.fillStyle = on > 0.5 ? '#00c2ff' : 'rgba(255,255,255,0.14)';
      rr(ctx, 990, y - 13, 52, 26, 14); ctx.fill();
      if (on > 0.5) {
        ctx.shadowColor = 'rgba(0,194,255,0.6)'; ctx.shadowBlur = 14;
        ctx.fillStyle = '#00c2ff';
        rr(ctx, 990, y - 13, 52, 26, 14); ctx.fill();
        ctx.shadowColor = 'transparent';
      }
      ctx.beginPath();
      ctx.arc(990 + 13 + on * 26, y, 10, 0, Math.PI * 2);
      ctx.fillStyle = '#fff'; ctx.fill();
      ctx.globalAlpha *= 0.35 + 0.65 * on;
      txt(ctx, label, 1060, y + 7, { size: 19.5, family: 'SGB', color: on > 0.5 ? '#e6f7ff' : '#7f95b5', align: 'left' });
      ctx.globalAlpha = p * (0.35 + 0.65 * on);
      txt(ctx, on > 0.5 ? 'OK' : '--', 1440, y + 7, { size: 15, family: 'JBMB', color: on > 0.5 ? '#00ff88' : '#5b6b8c', align: 'right' });
      ctx.globalAlpha = p;
    });
    ctx.restore();
  }

  // peaceful ripples
  if (L > aSilence - 0.3) {
    for (let i = 0; i < 3; i++) {
      const rp = ((L - aSilence) * 0.4 + i * 0.33) % 1;
      if (rp < 0) continue;
      ctx.beginPath();
      ctx.arc(W / 2, 520, 60 + rp * 240, 0, Math.PI * 2);
      ctx.strokeStyle = `rgba(0,255,136,${0.4 * (1 - rp)})`;
      ctx.lineWidth = 2.5;
      ctx.stroke();
    }
  }

  if (white > 0) {
    const wg = ctx.createRadialGradient(W / 2, H / 2, 0, W / 2, H / 2, H);
    wg.addColorStop(0, `rgba(234,255,255,${white})`);
    wg.addColorStop(1, `rgba(255,255,255,${white})`);
    ctx.fillStyle = wg;
    ctx.fillRect(0, 0, W, H);
  }
}

// ---------------------------------------------------------------- SCENE 17
export function s17(ctx, L, t) {
  const end = 49.4;
  const wipe = clamp01((L - (end - 1.0)) / 1.0);
  const aLaugh = A(17, 'laughing');
  const aColors = A(17, 'colors');
  const aGoblin = A(17, 'goblin');
  const aMorning = A(17, 'morning');
  const aLegit = A(17, 'legit');
  const aTwitch = A(17, 'twitch');

  // confetti
  for (let i = 0; i < 26; i++) {
    const p = ((L * 0.3 + hash(i + 8)) % 1);
    ctx.save();
    ctx.globalAlpha = 0.85 * (1 - p * 0.5);
    ctx.translate(hash(i) * W + (hash(i + 10) - 0.5) * 120 * p, -30 + p * 960);
    ctx.rotate(p * 9 + i);
    ctx.fillStyle = ['#ff5c8a', '#ffd35c', '#7dd8a8', '#9fc6ff', '#c9a3ff'][i % 5];
    rr(ctx, -6, -8, 12, 16, 3); ctx.fill();
    ctx.restore();
  }

  // relaxed figure + laptop
  ctx.save();
  ctx.translate(180, 500 + Math.sin(L * 1.6) * 8);
  ctx.strokeStyle = '#cfe0ff'; ctx.lineWidth = 7; ctx.lineCap = 'round';
  ctx.beginPath(); ctx.arc(0, -60, 26, 0, Math.PI * 2); ctx.stroke();
  ctx.beginPath(); ctx.moveTo(0, -34); ctx.lineTo(0, 30); ctx.stroke();
  ctx.beginPath(); ctx.moveTo(-30, -10); ctx.lineTo(30, -10); ctx.stroke();
  ctx.restore();
  ctx.save();
  ctx.translate(260, 620);
  ctx.fillStyle = '#232a4d';
  rr(ctx, -60, -40, 120, 74, 8); ctx.fill();
  ctx.fillStyle = 'rgba(0,229,255,0.8)';
  rr(ctx, -50, -32, 100, 58, 4); ctx.fill();
  ctx.restore();

  // HA HA HA
  if (L > aLaugh - 0.2) {
    'HA HA HA'.split('').forEach((ch, i) => {
      const p = beat(L, aLaugh - 0.2 + i * 0.06, 0.3);
      if (p <= 0 || ch === ' ') return;
      const bounce = Math.abs(Math.sin(L * 5.5 + i * 0.9));
      ctx.save();
      ctx.globalAlpha = p;
      ctx.translate(470 + i * 62, 130 - bounce * 34);
      ctx.scale(1 + bounce * 0.12, 1 - bounce * 0.08);
      txt(ctx, ch, 0, 0, {
        size: 58 + (i % 3) * 14, family: 'AB',
        color: ['#ffd35c', '#ff5c8a', '#7dd8a8'][i % 3],
        glow: 'rgba(255,211,92,0.35)',
      });
      ctx.restore();
    });
  }

  txt(ctx, 'I start laughing — real laughing', W / 2, 84, {
    size: 40, family: 'AB', color: '#ffe9b3', glow: 'rgba(255,211,92,0.5)',
    alpha: beat(L, aLaugh, 0.4),
  });

  // expectation vs reality
  if (L > aColors - 0.6) {
    const p = easeOut(beat(L, aColors - 0.6, 0.5));
    ctx.save();
    ctx.globalAlpha = p;
    ctx.translate(0, (1 - p) * 30);
    panel(ctx, 240, 220, 520, 260, { r: 22, fill: 'rgba(255,240,250,0.94)', border: 'rgba(255,92,138,0.4)' });
    txt(ctx, 'EXPECTATION · WHAT I THOUGHT', 270, 262, { size: 12.5, family: 'JBMB', color: '#c2497c', align: 'left' });
    ['brand colors', 'motivational quotes', 'posting consistently', 'aesthetic cafe'].forEach((chip, i) => {
      const cp = easeOutBack(beat(L, aColors + i * 0.3, 0.4));
      if (cp <= 0) return;
      ctx.save();
      ctx.globalAlpha = cp;
      ctx.translate(280 + (i % 2) * 240, 306 + Math.floor(i / 2) * 62);
      ctx.rotate((hash(i) - 0.5) * 0.06 + Math.sin(L * 1.5 + i) * 0.02);
      ctx.scale(0.8 + 0.2 * cp, 0.8 + 0.2 * cp);
      ctx.fillStyle = '#ffe3ef';
      rr(ctx, -105, -24, 210, 48, 24); ctx.fill();
      txt(ctx, chip, 0, 8, { size: 17.5, family: 'SGB', color: '#8f2d5c' });
      ctx.restore();
    });

    panel(ctx, 840, 220, 520, 260, { r: 22, fill: 'rgba(16,4,20,0.9)', border: 'rgba(143,123,255,0.5)', glow: 'rgba(143,123,255,0.25)' });
    txt(ctx, 'REALITY · 2:00 A.M.', 870, 262, { size: 12.5, family: 'JBMB', color: '#c9a3ff', align: 'left' });
    ['cyber-goblin wrestling', 'pajama pants', 'fraud bootcamp', 'raccoon landlords'].forEach((chip, i) => {
      const cp = easeOutBack(beat(L, aGoblin - 0.2 + i * 0.34, 0.4));
      if (cp <= 0) return;
      ctx.save();
      ctx.globalAlpha = cp;
      ctx.translate(880 + (i % 2) * 240, 306 + Math.floor(i / 2) * 62);
      ctx.rotate((hash(i + 3) - 0.5) * 0.14);
      ctx.scale(0.8 + 0.2 * cp, 0.8 + 0.2 * cp);
      ctx.fillStyle = 'rgba(143,123,255,0.16)';
      rr(ctx, -105, -24, 210, 48, 24); ctx.fill();
      ctx.strokeStyle = 'rgba(201,163,255,0.5)'; ctx.lineWidth = 1.5;
      rr(ctx, -105, -24, 210, 48, 24); ctx.stroke();
      txt(ctx, chip, 0, 8, { size: 17.5, family: 'SGB', color: '#e6ddff' });
      ctx.restore();
    });
    ctx.restore();
  }

  // sunrise
  if (L > aMorning - 0.8) {
    const p = beat(L, aMorning - 0.8, 0.6);
    ctx.save();
    ctx.globalAlpha = p;
    const rise = Math.sin(clamp01((L - aMorning) / 3) * Math.PI * 0.5) * 40;
    ctx.translate(W / 2, 700 - rise);
    ctx.shadowColor = 'rgba(255,179,71,0.8)'; ctx.shadowBlur = 90;
    ctx.beginPath(); ctx.arc(0, 0, 62, 0, Math.PI * 2);
    const sg = ctx.createRadialGradient(-16, -20, 4, 0, 0, 62);
    sg.addColorStop(0, '#fff3c4'); sg.addColorStop(0.7, '#ffb347'); sg.addColorStop(1, '#ff9a3c');
    ctx.fillStyle = sg; ctx.fill();
    ctx.shadowColor = 'transparent';
    txt(ctx, 'the next morning', 0, 106, { size: 30, family: 'CVB', color: '#ffd98a' });
    ctx.restore();
  }

  // cautious email
  if (L > aLegit - 1.2) {
    const p = easeOut(beat(L, aLegit - 1.2, 0.5));
    const tremble = L < aLegit + 3 ? Math.sin(L * 18) * 0.028 : 0;
    ctx.save();
    ctx.globalAlpha = p;
    ctx.translate(lerp(320, 0, p), 0);
    ctx.translate(1150, 600);
    ctx.rotate(tremble);
    panel(ctx, -235, -76, 470, 152, { r: 16, fill: 'rgba(255,255,255,0.95)' });
    txt(ctx, 'new email · subject:', -205, -44, { size: 13, family: 'JBM', color: '#7f8cab', align: 'left' });
    txt(ctx, '“Order Inquiry (Legit)”', -205, -6, { size: 25, family: 'AB', color: '#23262e', align: 'left' });
    txt(ctx, '“Hi! I run a coworking space… can we talk?”', -205, 34, { size: 22, family: 'CVB', color: '#5b6478', align: 'left' });
    txt(ctx, 'hmm…', 190, 58, { size: 24, family: 'CVB', color: '#0e9f6e', rotate: 0.2 });
    ctx.restore();
  }

  // twitching eye
  if (L > aTwitch - 0.2) {
    const p = beat(L, aTwitch - 0.2, 0.3);
    ctx.save();
    ctx.globalAlpha = p;
    ctx.translate(170 + Math.sin(L * 26) * 3, 560);
    ctx.strokeStyle = '#fff'; ctx.lineWidth = 5;
    ctx.beginPath(); ctx.ellipse(0, 0, 44, 24, 0, 0, Math.PI * 2); ctx.stroke();
    ctx.beginPath(); ctx.arc(Math.sin(L * 26) * 6, 0, 10, 0, Math.PI * 2);
    ctx.fillStyle = '#5c8bff'; ctx.fill();
    txt(ctx, 'my eye twitches', 0, 56, { size: 27, family: 'CVB', color: '#ffb3c8' });
    ctx.restore();
  }

  // sun wipe out
  if (wipe > 0) {
    ctx.save();
    ctx.beginPath();
    ctx.rect(0, 0, W, H);
    ctx.arc(W / 2, H * 0.62, wipe * 1900, 0, Math.PI * 2, true);
    const wg = ctx.createRadialGradient(W / 2, H * 0.62, 0, W / 2, H * 0.62, wipe * 1900);
    wg.addColorStop(0, '#fff7e0'); wg.addColorStop(1, '#ffca6a');
    ctx.fillStyle = wg;
    ctx.fill();
    ctx.restore();
  }
}

// ---------------------------------------------------------------- SCENE 18
export function s18(ctx, L, t, done = {}) {
  const aHop = A(18, 'hop');
  const aReal = A(18, 'real');
  const aDoor = A(18, 'frontdoor');
  const aFulfill = A(18, 'fulfill');
  const aReorder = A(18, 'reorder');
  const aUpgraded = A(18, 'upgraded');
  const aRules = A(18, 'rules');
  const aJoke = A(18, 'warehousejoke');
  const aNearMiss = A(18, 'nearmiss');
  const aEver = A(18, 'everget');
  const aDontShip = A(18, 'dontship');
  const aSpine = A(18, 'spine');
  const end = DATA_END;
  const outro = clamp01((L - (end - 2.2)) / 2.2);

  // big sun
  ctx.save();
  ctx.globalAlpha = 0.5 + 0.08 * Math.sin(L * 1.2);
  const sg = ctx.createRadialGradient(W / 2, H + 100, 60, W / 2, H + 100, 560);
  sg.addColorStop(0, '#fff3c4'); sg.addColorStop(0.55, '#ffca6a'); sg.addColorStop(1, '#ff9a3c');
  ctx.fillStyle = sg;
  ctx.beginPath(); ctx.arc(W / 2, H + 100, 420, 0, Math.PI * 2); ctx.fill();
  ctx.restore();

  // business card
  if (L > aHop) {
    const p = easeOutBack(beat(L, aHop, 0.5));
    const flip = clamp01((L - aHop - 0.2) / 0.9);
    ctx.save();
    ctx.translate(W / 2, 148);
    ctx.scale(p * Math.abs(Math.cos(flip * Math.PI)) ** 0.15, p);
    ctx.rotate(-0.01);
    const cg = ctx.createLinearGradient(-380, -70, 380, 70);
    cg.addColorStop(0, '#ffffff'); cg.addColorStop(1, '#ffe9c9');
    ctx.shadowColor = 'rgba(60,20,0,0.35)'; ctx.shadowBlur = 50; ctx.shadowOffsetY = 18;
    rr(ctx, -400, -72, 800, 144, 20);
    ctx.fillStyle = cg; ctx.fill();
    ctx.shadowColor = 'transparent'; ctx.shadowBlur = 0; ctx.shadowOffsetY = 0;
    txt(ctx, 'NEW CUSTOMER · VERIFIED', 0, -34, { size: 13, family: 'JBMB', color: '#b0793a' });
    txt(ctx, 'Downtown Coworking Co.', 0, 8, { size: 34, family: 'AB', color: '#23262e' });
    txt(ctx, 'they laughed at my jokes · they have a FRONT DOOR', 0, 48, { size: 27, family: 'CVB', color: '#0e9f6e' });
    ctx.restore();
  }

  // checklist card
  if (L > aReal) {
    const p = easeOut(beat(L, aReal, 0.5));
    ctx.save();
    ctx.globalAlpha = p;
    ctx.translate(lerp(-60, 120, easeOut(p)), 0);
    panel(ctx, 120, 300, 430, 270, { r: 20, fill: 'rgba(255,252,244,0.94)' });
    txt(ctx, 'HOW TO SPOT A REAL CUSTOMER', 150, 338, { size: 13, family: 'JBMB', color: '#b0793a', align: 'left' });
    const rows = [
      ['a website', aReal + 0.4],
      ['a phone number', aReal + 1.0],
      ['a normal address', aDoor - 1.6],
      ['a front door', aDoor - 0.6],
    ];
    rows.forEach(([label, at], i) => {
      const cp = beat(L, at, 0.35);
      const y = 380 + i * 44;
      ctx.save();
      ctx.globalAlpha *= 0.25 + 0.75 * cp;
      ctx.translate((1 - cp) * -20, 0);
      if (cp >= 1) {
        ctx.strokeStyle = '#0e9f6e'; ctx.lineWidth = 4; ctx.lineCap = 'round';
        rr(ctx, 150, y - 14, 22, 22, 5); ctx.stroke();
        ctx.beginPath(); ctx.moveTo(155, y - 3); ctx.lineTo(160, y + 4); ctx.lineTo(171, y - 10); ctx.stroke();
      } else {
        ctx.strokeStyle = 'rgba(35,38,46,0.35)'; ctx.lineWidth = 3;
        rr(ctx, 150, y - 14, 22, 22, 5); ctx.stroke();
      }
      txt(ctx, label, 190, y + 4, { size: 23, family: 'SGB', color: '#23262e', align: 'left' });
      ctx.restore();
    });
    ctx.restore();
  }

  // fulfill card
  if (L > aFulfill) {
    const p = easeOut(beat(L, aFulfill, 0.5));
    ctx.save();
    ctx.globalAlpha = p;
    ctx.translate(lerp(60, -120, easeOut(p)), 0);
    panel(ctx, 1050, 300, 430, 250, { r: 20, fill: 'rgba(6,20,14,0.85)', border: 'rgba(0,255,136,0.4)' });
    txt(ctx, 'BRANDED PLANNERS · FULFILLED', 1265, 340, { size: 12.5, family: 'JBMB', color: '#7dd8a8' });
    const cp = easeOut(beat(L, aFulfill + 0.2, 1.4));
    txt(ctx, String(Math.round(200 * cp)), 1265, 428, { size: 72, family: 'AB', color: '#00ff88', glow: 'rgba(0,255,136,0.5)' });
    rr(ctx, 1080, 466, 370, 12, 7);
    ctx.fillStyle = 'rgba(255,255,255,0.12)'; ctx.fill();
    if (cp > 0) {
      rr(ctx, 1080, 466, 370 * cp, 12, 7);
      ctx.fillStyle = '#00ff88'; ctx.fill();
    }
    if (L > aReorder - 0.3) {
      const rp = beat(L, aReorder - 0.3, 0.4);
      ctx.globalAlpha = p * rp;
      txt(ctx, 'reorder next month · OK', 1265, 516, {
        size: 22, family: 'AB', color: '#ffd35c',
        glow: 'rgba(255,211,92,0.5)', alpha: 0.75 + 0.25 * Math.sin(L * 3.5),
      });
    }
    ctx.restore();
  }

  // UPGRADED moment
  if (L > aUpgraded - 0.5) {
    const p = beat(L, aUpgraded - 0.5, 0.6);
    ctx.save();
    ctx.globalAlpha = p;
    ctx.translate(W / 2, 430);
    ctx.scale(0.6 + 0.4 * easeOutBack(p), 0.6 + 0.4 * easeOutBack(p));
    txt(ctx, 'IT UPGRADED ME.', 0, 0, { size: 88, family: 'AB', color: '#fff', glow: 'rgba(255,202,106,0.8)' });
    txt(ctx, '“if fraudsters target you… you built something real', 0, 52, { size: 30, family: 'CVB', color: '#ffe9c9' });
    txt(ctx, 'enough to be worth targeting.”', 0, 88, { size: 30, family: 'CVB', color: '#ffe9c9' });
    ctx.restore();
  }

  // growth chart
  if (L > aRules - 0.3) {
    const p = easeOut(beat(L, aRules - 0.3, 0.5));
    ctx.save();
    ctx.globalAlpha = p;
    panel(ctx, 420, 520, 760, 170, { r: 20, fill: 'rgba(8,10,20,0.8)' });
    txt(ctx, 'SECURITY RULES · PLAIN ENGLISH · VERIFYING REALITY', 450, 554, { size: 12.5, family: 'JBMB', color: '#9fc6ff', align: 'left' });
    const prog = clamp01((L - aRules) / 2.2);
    const pts = [];
    for (let i = 0; i <= 40; i++) {
      const q = i / 40;
      pts.push([450 + q * 700, 668 - Math.pow(q, 1.6) * 96]);
    }
    ctx.save();
    ctx.beginPath();
    const nPts = Math.max(2, Math.floor(pts.length * prog));
    ctx.moveTo(pts[0][0], pts[0][1]);
    for (let i = 1; i < nPts; i++) ctx.lineTo(pts[i][0], pts[i][1]);
    ctx.strokeStyle = '#00ff88';
    ctx.lineWidth = 5;
    ctx.shadowColor = 'rgba(0,255,136,0.6)'; ctx.shadowBlur = 12;
    ctx.stroke();
    ctx.shadowColor = 'transparent';
    if (prog >= 1) {
      ctx.beginPath(); ctx.arc(pts[pts.length - 1][0], pts[pts.length - 1][1], 8, 0, Math.PI * 2);
      ctx.fillStyle = '#ffd35c';
      ctx.shadowColor = '#ffd35c'; ctx.shadowBlur = 14;
      ctx.fill();
      ctx.shadowColor = 'transparent';
    }
    ctx.restore();
    ctx.restore();
  }

  // raccoon callback
  if (L > aJoke - 0.4) {
    const p = beat(L, aJoke - 0.4, 0.4);
    ctx.save();
    ctx.globalAlpha = p;
    ctx.translate(300, 800 + Math.sin(L * 1.5) * 6);
    ctx.rotate(-0.09);
    panel(ctx, -180, -60, 360, 120, { r: 16, fill: 'rgba(255,255,255,0.92)' });
    drawRaccoonHead(ctx, 0, -18, 0.5);
    txt(ctx, '“almost donated $12,000 of planners', 0, 22, { size: 22, family: 'CVB', color: '#23262e' });
    txt(ctx, 'to a raccoon warehouse”', 0, 48, { size: 22, family: 'CVB', color: '#23262e' });
    ctx.restore();
  }

  // moral card
  if (L > aNearMiss - 0.4) {
    const p = beat(L, aNearMiss - 0.4, 0.5);
    ctx.save();
    ctx.globalAlpha = p;
    ctx.translate(1150, 700);
    ctx.rotate(0.028);
    const mg = ctx.createLinearGradient(0, -80, 0, 80);
    mg.addColorStop(0, '#fff8ea'); mg.addColorStop(1, '#ffe9c9');
    panel(ctx, -240, -84, 480, 168, { r: 18, fill: mg });
    txt(ctx, 'THE MORAL', -210, -46, { size: 12, family: 'JBMB', color: '#b0793a', align: 'left' });
    txt(ctx, 'Wins feel amazing. Near-misses are', -210, -8, { size: 22, family: 'AB', color: '#4a2c10', align: 'left' });
    txt(ctx, 'where you become the person', -210, 26, { size: 22, family: 'AB', color: '#4a2c10', align: 'left' });
    txt(ctx, 'who can handle the wins.', -210, 60, { size: 22, family: 'AB', color: '#c2570f', align: 'left' });
    ctx.restore();
  }

  // final lines
  if (L > aEver - 0.6) {
    const p = beat(L, aEver - 0.6, 0.4);
    ctx.save();
    ctx.globalAlpha = p * (1 - outro);
    txt(ctx, 'if you ever get a massive order at 2:07 a.m.', W / 2, 700, { size: 34, family: 'CVB', color: '#3a1c08' });
    txt(ctx, 'to an abandoned warehouse…', W / 2, 738, { size: 34, family: 'CVB', color: '#3a1c08' });
    ctx.restore();
  }
  if (L > aDontShip - 0.3) {
    const pop = 1 + 0.3 * beat(L, aDontShip - 0.3, 0.25) * (1 - beat(L, aDontShip - 0.3, 0.6));
    ctx.save();
    ctx.globalAlpha = (1 - outro) * clamp01((L - aDontShip + 0.3) * 3);
    ctx.translate(W / 2, 800);
    ctx.scale(pop, pop);
    txt(ctx, 'DON\u2019T SHIP IT.', 0, 0, { size: 76, family: 'AB', color: '#ff4646', glow: 'rgba(255,70,70,0.55)' });
    ctx.restore();
  }
  if (L > aSpine - 0.4) {
    const p = easeOutBack(beat(L, aSpine - 0.4, 0.35));
    ctx.save();
    ctx.globalAlpha = (1 - outro) * clamp01(p * 1.4);
    ctx.translate(W / 2, 868);
    ctx.scale(p, p);
    const w1 = measure(ctx, 'SHIP YOUR ', { size: 84, family: 'AB' });
    const w2 = measure(ctx, 'SPINE', { size: 84, family: 'AB' });
    const w3 = measure(ctx, ' FIRST.', { size: 84, family: 'AB' });
    const total = w1 + w2 + w3;
    txt(ctx, 'SHIP YOUR ', -total / 2, 0, { size: 84, family: 'AB', color: '#fff', align: 'left', glow: 'rgba(0,255,136,0.5)' });
    txt(ctx, 'SPINE', -total / 2 + w1, 0, { size: 84, family: 'AB', color: '#00ff88', align: 'left', glow: 'rgba(0,255,136,0.6)' });
    txt(ctx, ' FIRST.', -total / 2 + w1 + w2, 0, { size: 84, family: 'AB', color: '#fff', align: 'left', glow: 'rgba(0,255,136,0.5)' });
    ctx.restore();
  }

  if (outro > 0) {
    ctx.fillStyle = `rgba(0,0,0,${outro * 0.92})`;
    ctx.fillRect(0, 0, W, H);
    if (outro > 0.5) {
      ctx.save();
      ctx.globalAlpha = clamp01((outro - 0.5) * 2.2);
      txt(ctx, 'THE END', W / 2, H / 2 - 30, { size: 18, family: 'JBMB', color: '#00ff88' });
      txt(ctx, 'SHIP YOUR SPINE FIRST', W / 2, H / 2 + 30, { size: 54, family: 'AB', color: '#fff' });
      txt(ctx, 'an interactive motion story · 10:32 · 18 scenes · word-synced', W / 2, H / 2 + 76, { size: 14, family: 'JBM', color: '#66718f' });
      ctx.restore();
    }
  }
}

function drawRaccoonHead(ctx, x, y, s) {
  ctx.save();
  ctx.translate(x, y);
  ctx.scale(s, s);
  ctx.fillStyle = '#6b6f7c';
  ctx.beginPath(); ctx.moveTo(-46, -28); ctx.lineTo(-28, -58); ctx.lineTo(-14, -30); ctx.closePath(); ctx.fill();
  ctx.beginPath(); ctx.moveTo(46, -28); ctx.lineTo(28, -58); ctx.lineTo(14, -30); ctx.closePath(); ctx.fill();
  ctx.beginPath(); ctx.arc(0, -20, 40, 0, Math.PI * 2);
  ctx.fillStyle = '#8b8f9c'; ctx.fill();
  ctx.fillStyle = '#3a3d47';
  ctx.beginPath(); ctx.ellipse(-16, -26, 14, 9, -0.3, 0, Math.PI * 2); ctx.fill();
  ctx.beginPath(); ctx.ellipse(16, -26, 14, 9, 0.3, 0, Math.PI * 2); ctx.fill();
  ctx.fillStyle = '#ffd35c';
  ctx.beginPath(); ctx.arc(-16, -26, 4.5, 0, Math.PI * 2); ctx.fill();
  ctx.beginPath(); ctx.arc(16, -26, 4.5, 0, Math.PI * 2); ctx.fill();
  ctx.fillStyle = '#e8e9ee';
  ctx.beginPath(); ctx.ellipse(0, -6, 14, 9, 0, 0, Math.PI * 2); ctx.fill();
  ctx.fillStyle = '#26282f';
  ctx.beginPath(); ctx.arc(0, -9, 3.5, 0, Math.PI * 2); ctx.fill();
  // top hat
  ctx.fillStyle = '#181a22';
  rr(ctx, -20, -76, 40, 30, 4); ctx.fill();
  rr(ctx, -30, -48, 60, 7, 3); ctx.fill();
  ctx.restore();
}

// end time injected by render.mjs
export let DATA_END = 85.2;
export function setEnd(v) { DATA_END = v; }
