/**
 * scenes1.mjs — offline renderers for scenes 1–9.
 * Each export: (ctx, L, t) where L = scene-local seconds, t = global seconds.
 */
import {
  W, H, DATA, anchorLocal, beat, easeOut, easeOutBack, hash, lerp, clamp01,
  rgba, mixHex, rr, panel, txt, typed, star, heart, note, measure,
} from './lib.mjs';

const A = anchorLocal;

// ---------------------------------------------------------------- SCENE 01
export function s01(ctx, L, t) {
  const end = 12.11;
  const out = clamp01((L - (end - 0.8)) / 0.8);

  ctx.save();
  ctx.translate(W / 2, H / 2);
  ctx.scale(1 + out * 1.6, 1 + out * 1.6);
  ctx.translate(-W / 2, -H / 2);

  // cutout blobs
  ctx.fillStyle = 'rgba(255,255,255,0.06)';
  rr(ctx, -60 + Math.sin(t * 0.7) * 20, 70, 340, 130, 90); ctx.fill();
  ctx.fillStyle = 'rgba(143,123,255,0.10)';
  rr(ctx, 1240 - Math.sin(t * 0.6) * 24, 160, 420, 150, 100); ctx.fill();
  ctx.fillStyle = 'rgba(0,194,255,0.07)';
  rr(ctx, 120, 570 + Math.sin(t * 0.8) * 12, 260, 110, 80); ctx.fill();

  // clock
  const cPop = easeOutBack(beat(L, 0.4, 0.5));
  if (cPop > 0) {
    ctx.save();
    ctx.translate(215, 185);
    ctx.scale(cPop, cPop);
    const pulse = 0.5 + 0.5 * Math.sin(L * 3.6);
    ctx.shadowColor = 'rgba(143,123,255,0.8)';
    ctx.shadowBlur = 20 + 26 * pulse;
    ctx.beginPath(); ctx.arc(0, 0, 86, 0, Math.PI * 2);
    ctx.fillStyle = 'rgba(10,12,34,0.9)'; ctx.fill();
    ctx.shadowColor = 'transparent';
    ctx.lineWidth = 7; ctx.strokeStyle = '#8f7bff'; ctx.stroke();
    ctx.lineWidth = 2; ctx.strokeStyle = 'rgba(255,255,255,0.15)';
    ctx.setLineDash([4, 10]); ctx.lineDashOffset = -L * 20;
    ctx.beginPath(); ctx.arc(0, 0, 74, 0, Math.PI * 2); ctx.stroke();
    ctx.setLineDash([]);
    // hour (2), minute (~07)
    ctx.lineCap = 'round';
    ctx.strokeStyle = '#fff'; ctx.lineWidth = 9;
    ctx.beginPath(); ctx.moveTo(0, 0);
    ctx.lineTo(Math.sin(1.047) * 46, -Math.cos(1.047) * 46); ctx.stroke();
    ctx.strokeStyle = '#00ff88'; ctx.lineWidth = 6;
    ctx.beginPath(); ctx.moveTo(0, 0);
    ctx.lineTo(Math.sin(0.733) * 62, -Math.cos(0.733) * 62); ctx.stroke();
    ctx.beginPath(); ctx.arc(0, 0, 8, 0, Math.PI * 2); ctx.fillStyle = '#00ff88'; ctx.fill();
    ctx.restore();
    if (L > 1) txt(ctx, '2:07 A.M.', 215, 320, { size: 26, family: 'JBMB', color: '#b9a8ff', glow: 'rgba(143,123,255,0.6)' });
  }

  // laptop on laundry basket (wobbling)
  const lPop = beat(L, A(1, 'laptop') - 0.6, 0.5);
  if (lPop > 0) {
    ctx.save();
    ctx.translate(760, 700);
    ctx.rotate(Math.sin(L * 2.6) * 0.055);
    ctx.globalAlpha = lPop;
    // basket
    ctx.fillStyle = '#3d2f56';
    ctx.beginPath();
    ctx.moveTo(-110, 0); ctx.lineTo(110, 0); ctx.lineTo(88, 92); ctx.lineTo(-88, 92);
    ctx.closePath(); ctx.fill();
    ctx.strokeStyle = 'rgba(255,255,255,0.16)'; ctx.lineWidth = 5;
    for (let i = 1; i <= 3; i++) {
      const yy = i * 22;
      ctx.beginPath(); ctx.moveTo(-102 + i * 4, yy); ctx.lineTo(102 - i * 4, yy); ctx.stroke();
    }
    for (let i = -2; i <= 2; i++) {
      ctx.beginPath(); ctx.moveTo(i * 40, 0); ctx.lineTo(i * 33, 92); ctx.stroke();
    }
    // laptop
    ctx.shadowColor = 'rgba(0,194,255,0.65)'; ctx.shadowBlur = 44;
    ctx.fillStyle = '#232a4d';
    rr(ctx, -135, -128, 270, 118, 10); ctx.fill();
    ctx.shadowColor = 'transparent';
    ctx.fillStyle = '#0b1030';
    rr(ctx, -122, -116, 244, 94, 6); ctx.fill();
    ctx.fillStyle = 'rgba(0,229,255,0.85)';
    ctx.beginPath();
    ctx.moveTo(-100, -40 + Math.sin(L * 2) * 4);
    ctx.lineTo(-60, -100); ctx.lineTo(-20, -52); ctx.lineTo(20, -96); ctx.lineTo(60, -44); ctx.lineTo(100, -88);
    ctx.strokeStyle = 'rgba(0,229,255,0.85)'; ctx.lineWidth = 3.5; ctx.stroke();
    ctx.fillStyle = '#2c3560';
    rr(ctx, -155, -12, 310, 16, 7); ctx.fill();
    ctx.restore();
    txt(ctx, 'office = laundry basket', 760, 830, { size: 30, family: 'CVB', color: '#9fe8ff', rotate: -0.05, alpha: lPop });
  }

  // cereal mug with pour particles
  const mPop = beat(L, A(1, 'cereal') - 0.5, 0.5);
  if (mPop > 0) {
    ctx.save();
    ctx.translate(1340, 705 + Math.sin(L * 1.8) * 8);
    ctx.globalAlpha = mPop;
    for (let i = 0; i < 9; i++) {
      const p = ((L * 1.4 + i * 0.13) % 1);
      ctx.globalAlpha = mPop * (1 - p);
      ctx.beginPath();
      ctx.arc(8 + (i % 3) * 13, -108 + p * 92, 5, 0, Math.PI * 2);
      ctx.fillStyle = ['#ffd35c', '#ff9a3c', '#fff5c0'][i % 3];
      ctx.fill();
    }
    ctx.globalAlpha = mPop;
    ctx.fillStyle = '#e8ecf5';
    rr(ctx, -52, -16, 104, 96, 14); ctx.fill();
    ctx.strokeStyle = '#e8ecf5'; ctx.lineWidth = 12;
    ctx.beginPath(); ctx.arc(62, 30, 26, -1.2, 1.2); ctx.stroke();
    ctx.fillStyle = '#c9a06a';
    rr(ctx, -42, -8, 84, 20, 9); ctx.fill();
    for (let i = 0; i < 5; i++) {
      ctx.beginPath();
      ctx.arc(-28 + i * 14, -2 + hash(i + L * 0.001) * 6, 4.5, 0, Math.PI * 2);
      ctx.fillStyle = '#8a5a2b'; ctx.fill();
    }
    ctx.restore();
    txt(ctx, 'coffee mug cereal', 1340, 832, { size: 30, family: 'CVB', color: '#ffd35c', rotate: 0.04, alpha: mPop });
  }

  // sparkle dots
  for (let i = 0; i < 5; i++) {
    const a = 0.3 + 0.5 * Math.sin(L * 2 + i * 1.7);
    star(ctx, 300 + i * 260, 130 + Math.sin(L + i) * 30, 9 + 3 * Math.sin(L * 3 + i), 3.4, 4, L + i);
    ctx.fillStyle = `rgba(255,255,255,${a * 0.8})`;
    ctx.fill();
  }

  // badge
  const bPop = easeOutBack(beat(L, A(1, 'entrepreneur') - 0.5, 0.5));
  if (bPop > 0) {
    ctx.save();
    ctx.translate(W / 2, 118);
    ctx.scale(bPop, bPop);
    ctx.rotate(-0.06 + Math.sin(L * 1.6) * 0.02);
    const bg = ctx.createLinearGradient(-190, 0, 190, 0);
    bg.addColorStop(0, '#00ff88'); bg.addColorStop(1, '#00c2ff');
    ctx.shadowColor = 'rgba(0,255,136,0.55)'; ctx.shadowBlur = 40;
    rr(ctx, -210, -34, 420, 68, 34);
    ctx.fillStyle = bg; ctx.fill();
    ctx.shadowColor = 'transparent';
    txt(ctx, 'ENTREPRENEUR NOW', 0, 10, { size: 34, family: 'AB', color: '#04120c' });
    ctx.restore();
  }

  txt(ctx, 'I need you to imagine this:', W / 2, 480, {
    size: 54, family: 'AB', color: '#fff', glow: 'rgba(143,123,255,0.6)',
    alpha: beat(L, 0.05, 0.5), scale: 0.8 + 0.2 * easeOutBack(beat(L, 0.05, 0.5)),
  });
  ctx.restore();

  if (out > 0) {
    ctx.fillStyle = `rgba(0,0,0,${out * 0.75})`;
    ctx.fillRect(0, 0, W, H);
  }
}

// ---------------------------------------------------------------- SCENE 02
export function s02(ctx, L, t) {
  const end = 17.4;
  const out = clamp01((L - (end - 0.7)) / 0.7);
  // bright product bg painted over dark palette
  const g = ctx.createLinearGradient(0, 0, W * 0.3, H);
  g.addColorStop(0, '#ffd9c7'); g.addColorStop(1, '#bff5e0');
  ctx.fillStyle = g; ctx.fillRect(0, 0, W, H);
  // floating shapes
  ctx.fillStyle = 'rgba(255,255,255,0.35)';
  ctx.beginPath(); ctx.arc(230 + Math.sin(t * 0.9) * 16, 150, 90, 0, Math.PI * 2); ctx.fill();
  ctx.save();
  ctx.translate(1330, 240); ctx.rotate(t * 0.35);
  ctx.fillStyle = 'rgba(255,255,255,0.3)';
  ctx.beginPath(); ctx.moveTo(0, -60); ctx.lineTo(52, 30); ctx.lineTo(-52, 30); ctx.closePath(); ctx.fill();
  ctx.restore();
  ctx.fillStyle = 'rgba(14,159,110,0.14)';
  rr(ctx, 200, 560, 150, 150, 36); ctx.save(); ctx.translate(275, 635); ctx.rotate(0.3); ctx.translate(-275, -635); ctx.fill(); ctx.restore();

  const aLaunched = A(2, 'launched');
  const aPlanners = A(2, 'planners');
  const aSticker = A(2, 'sticker');

  txt(ctx, 'a tiny online shop', W / 2, 140, {
    size: 54, family: 'AB', color: '#16324a',
    alpha: beat(L, aLaunched + 1.1, 0.5), scale: 0.85 + 0.15 * easeOutBack(beat(L, aLaunched + 1.1, 0.5)),
  });
  const tw = typed('custom productivity planners', aPlanners, 1.1, L);
  ctx.save();
  ctx.font = `700 34px JBM`;
  ctx.textAlign = 'center';
  ctx.fillStyle = '#0e9f6e';
  ctx.fillText(tw.s + (tw.done ? '' : '▌'), W / 2, 196);
  ctx.restore();

  // 3D carousel
  const cards = [
    { g1: '#ff9a76', g2: '#ff5c8a', label: 'Weekly Reset' },
    { g1: '#63e6be', g2: '#38b2ac', label: 'Invoice Tracker' },
    { g1: '#ffd35c', g2: '#ff9a3c', label: 'Deep Work' },
  ];
  const spin = L * 0.46;
  const cardPop = beat(L, aPlanners - 0.2, 0.5);
  for (let i = 0; i < 3; i++) {
    const ang = spin + (i * Math.PI * 2) / 3;
    const x = W / 2 + Math.sin(ang) * 350;
    const z = (Math.cos(ang) + 1) / 2; // 0 back .. 1 front
    const scale = 0.72 + 0.34 * z;
    const alpha = 0.35 + 0.65 * z;
    ctx.save();
    ctx.globalAlpha = alpha * cardPop * (1 - out);
    ctx.translate(x + out * (hash(i) - 0.5) * 900, 445 + out * (hash(i + 9) - 0.4) * 700);
    ctx.rotate(out * (hash(i + 4) - 0.5) * 5);
    ctx.scale(scale * (1 - out * 0.3), scale * (1 - out * 0.3));
    const cg = ctx.createLinearGradient(-150, -160, 150, 160);
    cg.addColorStop(0, cards[i].g1); cg.addColorStop(1, cards[i].g2);
    ctx.shadowColor = 'rgba(20,40,60,0.35)'; ctx.shadowBlur = 40; ctx.shadowOffsetY = 18;
    rr(ctx, -150, -160, 300, 320, 22);
    ctx.fillStyle = cg; ctx.fill();
    ctx.shadowColor = 'transparent'; ctx.shadowBlur = 0; ctx.shadowOffsetY = 0;
    // planner art
    ctx.fillStyle = 'rgba(255,255,255,0.9)';
    ctx.beginPath(); ctx.arc(0, -70, 40, 0, Math.PI * 2); ctx.fill();
    ctx.fillStyle = '#16324a';
    ctx.font = `700 34px SG`; ctx.textAlign = 'center';
    ctx.fillText(['7', '$', '★'][i], 0, -58);
    txt(ctx, cards[i].label, 0, 20, { size: 25, family: 'AB', color: '#fff' });
    ctx.fillStyle = 'rgba(255,255,255,0.55)';
    rr(ctx, -90, 44, 180, 9, 5); ctx.fill();
    rr(ctx, -65, 62, 130, 9, 5); ctx.fill();
    txt(ctx, 'funny prompt inside', 0, 118, { size: 27, family: 'CVB', color: 'rgba(255,255,255,0.95)' });
    ctx.restore();
  }

  // icon chips
  const chips = ['pencil draws checkmarks', 'sticky notes peel', 'passive-aggressive stickers'];
  chips.forEach((c, i) => {
    const p = easeOutBack(beat(L, aPlanners + 0.4 + i * 0.5, 0.45)) * (1 - out);
    if (p <= 0) return;
    ctx.save();
    ctx.globalAlpha = p;
    ctx.translate(480 + i * 330, 700);
    ctx.rotate((hash(i) - 0.5) * 0.1);
    ctx.fillStyle = 'rgba(255,255,255,0.78)';
    rr(ctx, -145, -26, 290, 52, 16); ctx.fill();
    txt(ctx, c, 0, 8, { size: 19, family: 'SGB', color: '#16324a' });
    ctx.restore();
  });

  // THE sticker
  const sPop = easeOutBack(beat(L, aSticker, 0.5)) * (1 - out);
  if (sPop > 0) {
    ctx.save();
    ctx.translate(1310, 300 + Math.sin(L * 2) * 5);
    ctx.rotate(0.14);
    ctx.scale(sPop, sPop);
    ctx.shadowColor = 'rgba(0,0,0,0.35)'; ctx.shadowBlur = 26; ctx.shadowOffsetY = 10;
    rr(ctx, -190, -66, 380, 132, 16);
    ctx.fillStyle = '#fff'; ctx.fill();
    ctx.shadowColor = 'transparent'; ctx.shadowBlur = 0; ctx.shadowOffsetY = 0;
    ctx.strokeStyle = 'rgba(217,43,58,0.35)'; ctx.lineWidth = 3;
    rr(ctx, -178, -54, 356, 108, 10); ctx.stroke();
    txt(ctx, '“Did you actually send', 0, -12, { size: 24, family: 'SGB', color: '#d92b3a' });
    txt(ctx, 'that invoice?”', 0, 26, { size: 24, family: 'SGB', color: '#d92b3a' });
    txt(ctx, 'hmm?', 150, 48, { size: 26, family: 'CVB', color: '#0e9f6e', rotate: 0.2 });
    ctx.restore();
  }

  // dark narration strip
  ctx.fillStyle = `rgba(10,16,30,${0.72 * (1 - out * 0.6)})`;
  rr(ctx, 130, 764, 1340, 96, 18); ctx.fill();
  if (out > 0) { ctx.fillStyle = `rgba(255,255,255,${out * 0.5})`; ctx.fillRect(0, 0, W, H); }
}

// ---------------------------------------------------------------- SCENE 03
export function s03(ctx, L, t) {
  const end = 8.3;
  const flash = clamp01((L - (end - 0.5)) / 0.5);
  const press = 0.5 + 0.5 * Math.sin(L * Math.PI / 0.45);
  const aRefresh = A(3, 'refresh');
  const aMaybe = A(3, 'maybe2');
  const aMom = A(3, 'mom');

  // neon grid
  ctx.save();
  ctx.strokeStyle = 'rgba(0,229,255,0.10)'; ctx.lineWidth = 1.5;
  const off = (L * 26) % 80;
  for (let x = -80 + off; x < W + 80; x += 80) { ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x, H); ctx.stroke(); }
  for (let y = -80 + off; y < H + 80; y += 80) { ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(W, y); ctx.stroke(); }
  ctx.restore();

  // headline
  txt(ctx, 'refreshing… again', W / 2, 88, {
    size: 40, family: 'AB', color: '#aef1ff', glow: 'rgba(0,229,255,0.7)',
    alpha: beat(L, aRefresh - 0.5, 0.5),
  });

  // browser window
  const wPop = easeOutBack(beat(L, 0.2, 0.5));
  ctx.save();
  ctx.translate(W / 2, 430);
  ctx.scale(wPop * (1 + flash * 0.25), wPop * (1 + flash * 0.25));
  ctx.translate(-W / 2, -430);
  panel(ctx, 220, 130, 1160, 600, {
    r: 22, fill: 'rgba(10,16,34,0.92)', border: 'rgba(0,229,255,0.25)',
    glow: flash > 0 ? `rgba(255,255,255,${flash})` : 'rgba(0,229,255,0.2)', shadowBlur: 60,
  });
  // title bar
  ctx.fillStyle = 'rgba(255,255,255,0.05)';
  rr(ctx, 220, 130, 1160, 58, { r: 22 }); ctx.fill();
  ['#ff5f57', '#febc2e', '#28c840'].forEach((c, i) => {
    ctx.beginPath(); ctx.arc(254 + i * 26, 159, 7, 0, Math.PI * 2); ctx.fillStyle = c; ctx.fill();
  });
  txt(ctx, 'store-dashboard-dot-com/orders', 640, 166, { size: 15, family: 'JBM', color: '#9fe8ff', align: 'left' });
  // spinner
  ctx.save();
  ctx.translate(1330, 159); ctx.rotate(L * 7);
  ctx.strokeStyle = '#00e5ff'; ctx.lineWidth = 4;
  ctx.beginPath(); ctx.arc(0, 0, 11, 0, Math.PI * 1.4); ctx.stroke();
  ctx.restore();

  // ORDERS + refresh button
  txt(ctx, 'ORDERS', 280, 268, { size: 30, family: 'AB', color: '#dfeaff', align: 'left' });
  const bx = 1180, by = 226;
  ctx.save();
  ctx.translate(bx + 90, by + 26);
  ctx.scale(1 - press * 0.08, 1 - press * 0.08);
  ctx.translate(-(bx + 90), -(by + 26));
  ctx.fillStyle = 'rgba(0,229,255,0.14)';
  rr(ctx, bx, by, 180, 52, 12); ctx.fill();
  ctx.strokeStyle = 'rgba(0,229,255,0.5)'; ctx.lineWidth = 1.5;
  rr(ctx, bx, by, 180, 52, 12); ctx.stroke();
  txt(ctx, 'REFRESH', bx + 78, by + 33, { size: 19, family: 'SGB', color: '#aef1ff' });
  ctx.save();
  ctx.translate(bx + 92, by + 26); ctx.rotate(L * 5);
  ctx.strokeStyle = '#aef1ff'; ctx.lineWidth = 3.5;
  ctx.beginPath(); ctx.arc(0, 0, 12, 0.5, Math.PI * 1.6); ctx.stroke();
  ctx.restore();
  // cursor
  ctx.save();
  ctx.translate(bx + 218 - press * 8, by + 62 - press * 8);
  ctx.rotate(-0.25);
  ctx.fillStyle = '#fff';
  ctx.beginPath();
  ctx.moveTo(0, 0); ctx.lineTo(0, 34); ctx.lineTo(9, 26); ctx.lineTo(16, 40); ctx.lineTo(22, 36); ctx.lineTo(15, 24); ctx.lineTo(26, 22);
  ctx.closePath(); ctx.fill();
  ctx.restore();
  ctx.restore();

  // order cards
  const cards = [
    { at: aMaybe - 0.4, tag: 'ORDER #1', big: '1', sub: 'just paid · planners ×1', col: '#00ff88', border: 'rgba(0,255,136,0.45)' },
    { at: aMaybe + 0.5, tag: 'ORDER #2', big: '?', sub: '…if my mom gets excited', col: '#5b6b8c', border: 'rgba(255,255,255,0.08)' },
  ];
  cards.forEach((c, i) => {
    const p = easeOutBack(beat(L, c.at, 0.5));
    if (p <= 0) return;
    ctx.save();
    ctx.globalAlpha = clamp01(p * 1.5);
    ctx.translate(320 + i * 490, 470);
    ctx.scale(0.9 + 0.1 * p, 0.9 + 0.1 * p);
    panel(ctx, -220, -90, 440, 200, { r: 20, fill: 'rgba(14,20,40,0.9)', border: c.border });
    txt(ctx, c.tag, 0, -46, { size: 14, family: 'JBM', color: '#7f95b5' });
    txt(ctx, c.big, 0, 42, { size: 88, family: 'AB', color: c.col, glow: c.big === '1' ? 'rgba(0,255,136,0.5)' : undefined });
    txt(ctx, c.sub, 0, 86, { size: 17, family: 'SGM', color: '#9fb3d9' });
    ctx.restore();
  });

  // mom hearts rising
  if (L > aMom - 0.5) {
    for (let i = 0; i < 7; i++) {
      const p = ((L - aMom) * 0.42 + i * 0.14) % 1;
      if (p < 0) continue;
      ctx.save();
      ctx.globalAlpha = (1 - p) * 0.9;
      ctx.translate(370 + i * 150 + Math.sin(p * 6 + i) * 24, 620 - p * 320);
      ctx.scale(1.1 + (i % 3) * 0.35, 1.1 + (i % 3) * 0.35);
      heart(ctx, 0, 0, 34);
      ctx.fillStyle = '#ff6ea9'; ctx.fill();
      ctx.restore();
    }
  }
  ctx.restore();

  // thought bubble
  const bPop = easeOutBack(beat(L, aMaybe - 0.8, 0.45));
  if (bPop > 0) {
    ctx.save();
    ctx.translate(1080, 660);
    ctx.rotate(-0.03);
    ctx.scale(bPop, bPop);
    ctx.fillStyle = 'rgba(255,255,255,0.92)';
    rr(ctx, -170, -34, 340, 68, 30); ctx.fill();
    ctx.beginPath(); ctx.arc(-150, 52, 9, 0, Math.PI * 2); ctx.fill();
    ctx.beginPath(); ctx.arc(-120, 70, 5, 0, Math.PI * 2); ctx.fill();
    txt(ctx, 'one order… maybe two?', 0, 4, { size: 27, family: 'CVB', color: '#122' });
    ctx.restore();
  }

  if (flash > 0) {
    ctx.fillStyle = `rgba(255,255,255,${Math.min(1, flash * 2.2)})`;
    ctx.fillRect(0, 0, W, H);
  }
}

// ---------------------------------------------------------------- SCENE 04
export function s04(ctx, L, t) {
  const end = 22.5;
  const out = clamp01((L - (end - 1.0)) / 1.0);
  const aUpdates = A(4, 'updates');
  const aSingle = A(4, 'single');
  const a500 = A(4, 'fivehundred');
  const aTotal = A(4, 'total');
  const aWhisper = A(4, 'whisper');

  ctx.save();
  if (out > 0) { ctx.translate(W / 2, H / 2); ctx.scale(1 + out * 1.6, 1 + out * 1.6); ctx.translate(-W / 2, -H / 2); }

  // speed lines
  ctx.save();
  ctx.translate(W / 2, H * 0.46);
  ctx.rotate(L * 0.06);
  for (let i = 0; i < 44; i++) {
    const a = (i / 44) * Math.PI * 2;
    ctx.rotate(Math.PI * 2 / 44);
    ctx.fillStyle = i % 2 ? 'rgba(255,255,255,0.06)' : 'rgba(255,255,255,0.025)';
    ctx.beginPath();
    ctx.moveTo(90, -5); ctx.lineTo(1200, -26); ctx.lineTo(1200, 26); ctx.lineTo(90, 5);
    ctx.closePath(); ctx.fill();
  }
  ctx.restore();

  // pink halo
  const halo = ctx.createRadialGradient(W / 2, H * 0.46, 0, W / 2, H * 0.46, 300 + Math.sin(L * 1.5) * 30);
  halo.addColorStop(0, 'rgba(255,0,110,0.25)');
  halo.addColorStop(1, 'rgba(255,0,110,0)');
  ctx.fillStyle = halo;
  ctx.fillRect(0, 0, W, H);

  // headline
  const hP = beat(L, aUpdates, 0.03 * 24);
  if (hP > 0) {
    ctx.save();
    ctx.translate(W / 2, 84);
    'THEN MY SCREEN UPDATES.'.split('').forEach((ch, i) => {
      const p = beat(L, aUpdates + i * 0.028, 0.4);
      if (p <= 0) return;
      ctx.save();
      ctx.translate((i - 11.5) * 21, 0);
      ctx.rotate((1 - p) * 3);
      ctx.scale(0.2 + 0.8 * p, 0.2 + 0.8 * p);
      ctx.globalAlpha = p;
      txt(ctx, ch, 0, 0, { size: 40, family: 'AB', color: '#fff', glow: 'rgba(255,0,110,0.8)' });
      ctx.restore();
    });
    ctx.restore();
  }

  // order card slam
  const slam = beat(L, aSingle - 0.35, 0.45);
  if (slam > 0) {
    const shake = L > aSingle + 0.15 && L < aSingle + 1.0;
    const sx = shake ? (hash(Math.floor(L * 90)) - 0.5) * 12 : 0;
    const sy = shake ? (hash(Math.floor(L * 90) + 50) - 0.5) * 12 : 0;
    ctx.save();
    ctx.translate(W / 2 + sx, H * 0.47 + sy);
    const e = easeOut(clamp01(slam));
    ctx.translate(0, (1 - e) * -520);
    ctx.scale(1 + out * 2.2, 1 + out * 2.2);
    ctx.globalAlpha = clamp01(slam * 2) * (1 - out);
    const cg = ctx.createLinearGradient(-380, -260, 380, 260);
    cg.addColorStop(0, '#7c3aed'); cg.addColorStop(1, '#ff006e');
    ctx.shadowColor = 'rgba(255,0,110,0.4)'; ctx.shadowBlur = 90; ctx.shadowOffsetY = 30;
    rr(ctx, -380, -250, 760, 500, 30);
    ctx.fillStyle = cg; ctx.fill();
    ctx.shadowColor = 'transparent'; ctx.shadowBlur = 0; ctx.shadowOffsetY = 0;
    ctx.strokeStyle = 'rgba(255,255,255,0.14)'; ctx.lineWidth = 4;
    rr(ctx, -380, -250, 760, 500, 30); ctx.stroke();

    txt(ctx, 'NEW ORDER · UNEXPECTED', 0, -186, { size: 17, family: 'JBM', color: 'rgba(255,255,255,0.75)' });
    // 500 counter
    const cp = easeOut(beat(L, a500, 1.4));
    const val = Math.round(500 * cp);
    ctx.save();
    if (cp > 0 && cp < 1) ctx.globalAlpha *= 0.75;
    txt(ctx, String(val), 0, -46, { size: 168, family: 'AB', color: '#fff', glow: 'rgba(255,255,255,0.45)' });
    ctx.restore();
    // PLANNERS spaced
    ctx.save();
    ctx.font = `400 30px AB`;
    ctx.fillStyle = '#ffd6e9';
    const word = 'PLANNERS';
    const spacing = 14;
    const tw = word.split('').reduce((a, ch) => a + ctx.measureText(ch).width + spacing, -spacing);
    let x = -tw / 2;
    ctx.textAlign = 'left';
    for (const ch of word) {
      ctx.fillText(ch, x, 8);
      x += ctx.measureText(ch).width + spacing;
    }
    ctx.restore();
    // $12,480
    const dPop = easeOutBack(beat(L, aTotal, 0.5));
    if (dPop > 0) {
      ctx.save();
      ctx.translate(0, 128);
      ctx.scale(dPop, dPop);
      txt(ctx, '$12,480', 0, 0, { size: 84, family: 'AB', color: '#00ff88', glow: 'rgba(0,255,136,0.6)', rotate: (1 - dPop) * -0.15 });
      ctx.restore();
    }
    ctx.restore();
  }

  // dollar rain
  if (L > aTotal) {
    ctx.font = `400 34px AB`;
    ctx.textAlign = 'center';
    for (let i = 0; i < 18; i++) {
      const p = ((L - aTotal) * 0.45 + hash(i)) % 1;
      ctx.save();
      ctx.globalAlpha = 0.85 * (1 - p * 0.7);
      ctx.translate(50 + i * 88, -40 + p * 990);
      ctx.rotate(p * 6 + i);
      ctx.fillStyle = '#7dffa8';
      ctx.fillText('$', 0, 0);
      ctx.restore();
    }
  }

  // impact stars
  if (L > aSingle) {
    for (let i = 0; i < 10; i++) {
      const ang = (i / 10) * Math.PI * 2 + L * 0.5;
      const rad = 300 + Math.sin(L * 2 + i) * 60;
      ctx.save();
      ctx.translate(W / 2 + Math.cos(ang) * rad, H * 0.46 + Math.sin(ang) * rad * 0.72);
      ctx.rotate(L * 2 + i);
      star(ctx, 0, 0, 22 + (i % 3) * 7, 8, 4, 0);
      ctx.fillStyle = '#ffd35c';
      ctx.shadowColor = 'rgba(255,211,92,0.8)'; ctx.shadowBlur = 20;
      ctx.fill();
      ctx.restore();
    }
  }

  // comic burst
  if (L > aWhisper - 0.4) {
    const bPop = easeOutBack(beat(L, aWhisper - 0.4, 0.4));
    ctx.save();
    ctx.translate(W / 2, 792);
    ctx.rotate(-0.05);
    ctx.scale(bPop * (1 + 0.03 * Math.sin(L * 6)), bPop * (1 + 0.03 * Math.sin(L * 6)));
    txt(ctx, '“FIVE… HUNDRED?!”', 6, 6, { size: 92, family: 'AB', color: 'rgba(0,229,255,0.9)' });
    txt(ctx, '“FIVE… HUNDRED?!”', -6, -6, { size: 92, family: 'AB', color: 'rgba(124,58,237,0.9)' });
    txt(ctx, '“FIVE… HUNDRED?!”', 0, 0, { size: 92, family: 'AB', color: '#ff006e', glow: 'rgba(255,0,110,0.6)' });
    ctx.restore();
  }
  ctx.restore();

  if (out > 0) {
    ctx.fillStyle = `rgba(0,0,0,${out * 0.6})`;
    ctx.fillRect(0, 0, W, H);
  }
}

// ---------------------------------------------------------------- SCENE 05
function ekgWave(x) {
  const cycle = (x % 1.1) / 1.1;
  if (cycle < 0.08) return Math.sin((cycle / 0.08) * Math.PI) * 0.16;
  if (cycle < 0.12) return -((cycle - 0.08) / 0.04) * 0.28;
  if (cycle < 0.16) return -0.28 + ((cycle - 0.12) / 0.04) * 1.28;
  if (cycle < 0.2) return 1 - ((cycle - 0.16) / 0.04) * 1.55;
  if (cycle < 0.24) return -0.55 + ((cycle - 0.2) / 0.04) * 0.55;
  if (cycle < 0.45) return Math.sin(((cycle - 0.24) / 0.21) * Math.PI) * 0.18;
  return 0;
}

export function s05(ctx, L, t) {
  const end = 22.9;
  const flat = beat(L, end - 1.4, 0.7) > 0;
  const glitch = beat(L, end - 0.6, 0.6);
  const aParkour = A(5, 'parkour');
  const aWifi = A(5, 'wifi');
  const aChair = A(5, 'chair');
  const aElliot = A(5, 'elliot');

  // ekg grid
  ctx.strokeStyle = 'rgba(57,255,136,0.07)'; ctx.lineWidth = 1;
  for (let x = 0; x < W; x += 44) { ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x, H); ctx.stroke(); }
  for (let y = 0; y < H; y += 44) { ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(W, y); ctx.stroke(); }

  // ekg line
  ctx.save();
  ctx.strokeStyle = flat ? 'rgba(57,255,136,0.75)' : '#39ff88';
  ctx.lineWidth = 3.4;
  ctx.shadowColor = '#39ff88'; ctx.shadowBlur = 16;
  ctx.beginPath();
  for (let x = 0; x <= W; x += 6) {
    const ph = L * 1.5 + x * 0.0028;
    const y = H / 2 + 20 - (flat ? Math.sin(ph) * 2 : ekgWave(ph) * 300);
    x === 0 ? ctx.moveTo(x, y) : ctx.lineTo(x, y);
  }
  ctx.stroke();
  ctx.restore();

  // headline
  txt(ctx, 'my heart starts doing PARKOUR', W / 2, 76, {
    size: 46, family: 'AB', color: '#ff5c8a', glow: 'rgba(255,0,110,0.6)',
    alpha: beat(L, aParkour, 0.4),
  });

  // parkour heart
  if (L > aParkour && glitch < 1) {
    const tt = Math.max(0, L - aParkour);
    const hop = 0.62;
    const hopN = Math.floor(tt / hop);
    const hopP = (tt % hop) / hop;
    const xs = [0, 1, 2, 3, 1, 2, 0, 3, 2, 1, 3, 0];
    const xi = xs[hopN % xs.length];
    const xj = xs[(hopN + 1) % xs.length];
    const x = 250 + lerp(xi, xj, hopP) * 320;
    const arc = Math.sin(hopP * Math.PI);
    // platforms
    for (let i = 0; i < 4; i++) {
      const px = 210 + i * 320;
      const py = 660 + Math.sin(i * 2.1) * 36 + Math.sin(L * 1.2 + i) * 4;
      panel(ctx, px - 65, py, 130, 44, { r: 12, fill: 'rgba(57,255,136,0.16)', border: 'rgba(57,255,136,0.4)', shadow: false });
      txt(ctx, ['ORDERS', 'PAYMENT', 'SHIPMENT', 'THOUGHTS'][i], px, py + 28, { size: 15, family: 'JBMB', color: '#9fe8b8' });
    }
    ctx.save();
    ctx.translate(x, 620 - arc * 130 - 30);
    ctx.rotate(hopP * Math.PI * 2);
    const s = 84 * (1 + arc * 0.16);
    ctx.shadowColor = 'rgba(255,0,110,0.8)'; ctx.shadowBlur = 40;
    heart(ctx, 0, 0, s);
    ctx.fillStyle = '#ff2b64'; ctx.fill();
    ctx.restore();
    // stress dashes
    for (let i = 0; i < 8; i++) {
      const ang = (i / 8) * Math.PI * 2 + tt * 0.9;
      txt(ctx, '〰', x + Math.cos(ang) * 96, 620 - arc * 130 - 30 + Math.sin(ang) * 74, {
        size: 20, color: 'rgba(255,92,138,0.6)', alpha: 0.4 + 0.4 * Math.sin(tt * 6 + i),
      });
    }
  }

  // split cards
  if (L > aElliot - 0.3) {
    const p = easeOutBack(beat(L, aElliot - 0.3, 0.5));
    ctx.save();
    ctx.globalAlpha = p;
    ctx.translate(lerp(-80, 90, easeOut(p)), 0);
    panel(ctx, 90, 150, 470, 190, { r: 20, fill: 'rgba(6,20,12,0.82)', border: 'rgba(0,255,136,0.35)' });
    txt(ctx, 'ORDER DETAILS · COLD FACTS', 325, 190, { size: 13, family: 'JBMB', color: '#39ff88' });
    const rows = [['Planners', '500'], ['Total', '$12,480'], ['Customer', '“Elliot Graye”'], ['Email', 'looks legit']];
    rows.forEach((r, i) => {
      const col = i % 2, row = Math.floor(i / 2);
      txt(ctx, r[0], 130 + col * 230, 236 + row * 44, { size: 19, family: 'SGM', color: '#cfe9dd', align: 'left' });
      txt(ctx, r[1], 130 + col * 230 + 110, 236 + row * 44, { size: 19, family: 'SGB', color: '#fff', align: 'left' });
    });
    ctx.restore();

    const p2 = easeOutBack(beat(L, aElliot + 0.4, 0.5));
    ctx.save();
    ctx.globalAlpha = p2;
    ctx.translate(lerp(90, -90, easeOut(p2)), 0);
    panel(ctx, W - 520, 170, 430, 200, { r: 20, fill: 'rgba(60,6,26,0.6)', border: 'rgba(255,0,110,0.5)' });
    txt(ctx, 'INTERNAL MONOLOGUE · PANIC', W - 305, 210, { size: 13, family: 'JBMB', color: '#ff5c8a' });
    txt(ctx, '“a person with Wi-Fi', W - 305, 260, { size: 30, family: 'CVB', color: '#ffd6e9' });
    txt(ctx, 'and a dream”', W - 305, 298, { size: 30, family: 'CVB', color: '#ffd6e9' });
    for (let i = 0; i < 12; i++) {
      const h = 10 + hash(i) * 34 * (0.5 + 0.5 * Math.sin(L * 8 + i));
      ctx.fillStyle = 'rgba(255,0,110,0.7)';
      ctx.fillRect(W - 480 + i * 15, 350 - h, 5, h);
    }
    ctx.restore();
  }

  // dream cloud
  if (L > aChair - 0.7) {
    const p = beat(L, aChair - 0.7, 0.5);
    ctx.save();
    ctx.globalAlpha = p;
    ctx.translate(W / 2, 210 + Math.sin(L * 1.6) * 10);
    const gg = ctx.createRadialGradient(0, 0, 0, 0, 0, 300);
    gg.addColorStop(0, 'rgba(255,215,130,0.3)');
    gg.addColorStop(1, 'rgba(255,215,130,0)');
    ctx.fillStyle = gg;
    ctx.fillRect(-300, -190, 600, 380);
    // chair icon
    ctx.fillStyle = '#ffe9b3';
    rr(ctx, -34, -74, 68, 10, 4); ctx.fill();          // back bar
    rr(ctx, -34, -74, 10, 74, 4); ctx.fill();           // back post
    rr(ctx, -34, -14, 68, 12, 5); ctx.fill();           // seat
    rr(ctx, -30, -2, 9, 40, 3); ctx.fill();             // legs
    rr(ctx, 21, -2, 9, 40, 3); ctx.fill();
    ctx.shadowColor = 'rgba(255,215,130,0.8)'; ctx.shadowBlur = 40;
    rr(ctx, -34, -74, 68, 10, 4); ctx.fill();
    ctx.shadowColor = 'transparent';
    txt(ctx, 'LUMBAR SUPPORT…', 0, 56, { size: 36, family: 'AB', color: '#ffe9b3', glow: 'rgba(255,215,130,0.7)' });
    txt(ctx, 'adult dream achieved', 0, 96, { size: 28, family: 'CVB', color: '#ffd98a' });
    ctx.restore();
  }

  if (L > aWifi - 0.2) {
    txt(ctx, 'Wi-Fi and a dream', W / 2, 640, {
      size: 40, family: 'AB', color: '#9fe8ff', glow: 'rgba(0,229,255,0.65)',
      alpha: 0.75 + 0.25 * Math.sin(L * 3),
    });
  }

  // glitch bands
  if (glitch > 0) {
    for (let i = 0; i < 6; i++) {
      ctx.fillStyle = i % 2 ? 'rgba(0,255,136,0.14)' : 'rgba(255,0,110,0.14)';
      ctx.fillRect((hash(i + 7) - 0.5) * 160 * glitch, hash(i + 3) * H, W, 10 + hash(i) * 30);
    }
  }
}

// ---------------------------------------------------------------- SCENE 06
export function s06(ctx, L, t) {
  const end = 29.2;
  const crumple = clamp01((L - (end - 0.8)) / 0.8);
  const aIndustrial = A(6, 'industrial');
  const aSuite = A(6, 'suite');
  const aMap = A(6, 'map');
  const aWarehouse = A(6, 'warehouse');
  const aRaccoon = A(6, 'raccoon');

  ctx.save();
  ctx.translate(W / 2, H / 2);
  ctx.scale(1 - crumple * 0.15, 1 - crumple * 0.15);
  ctx.rotate(-crumple * 0.05);
  ctx.translate(-W / 2, -H / 2);

  // zooming map
  const zoom = 1 + 0.35 * (0.5 + 0.5 * Math.sin(L * 0.24));
  ctx.save();
  ctx.translate(W / 2, H / 2);
  ctx.scale(zoom, zoom);
  ctx.translate(-W / 2, -H / 2);
  const g = ctx.createLinearGradient(0, 0, 0, H);
  g.addColorStop(0, '#0d1017'); g.addColorStop(1, '#090a10');
  ctx.fillStyle = g; ctx.fillRect(-100, -100, W + 200, H + 200);
  const streets = [
    [-50, 220, 300, 190, 700, 260, 1650, 200], [-50, 460, 400, 500, 900, 420, 1650, 480],
    [-50, 700, 500, 660, 1100, 740, 1650, 690], [240, -50, 200, 300, 300, 600, 240, 950],
    [620, -50, 660, 300, 580, 620, 640, 950], [1050, -50, 1000, 300, 1120, 600, 1060, 950],
    [1380, -50, 1420, 300, 1330, 620, 1400, 950],
  ];
  streets.forEach((s2, i) => {
    ctx.strokeStyle = i % 2 ? 'rgba(255,207,92,0.16)' : 'rgba(160,180,220,0.14)';
    ctx.lineWidth = i % 2 ? 12 : 8;
    ctx.beginPath();
    ctx.moveTo(s2[0], s2[1]);
    ctx.bezierCurveTo(s2[2], s2[3], s2[4], s2[5], s2[6], s2[7]);
    ctx.stroke();
  });
  for (let i = 0; i < 14; i++) {
    ctx.fillStyle = 'rgba(120,140,180,0.06)';
    ctx.strokeStyle = 'rgba(160,180,220,0.08)';
    ctx.lineWidth = 1;
    rr(ctx, hash(i) * 1400 + 20, hash(i + 20) * 740 + 30, 40 + hash(i + 5) * 90, 30 + hash(i + 9) * 60, 4);
    ctx.fill(); ctx.stroke();
  }
  ctx.setLineDash([8, 6]);
  ctx.strokeStyle = 'rgba(255,70,70,0.4)';
  ctx.strokeRect(1050, 380, 200, 140);
  ctx.setLineDash([]);
  ctx.restore();

  // warehouse silhouette
  if (L > aWarehouse - 0.6) {
    const p = easeOut(beat(L, aWarehouse - 0.6, 0.5));
    ctx.save();
    ctx.globalAlpha = p;
    ctx.translate(W / 2, 385 + Math.sin(L * 0.9) * 4);
    ctx.shadowColor = 'rgba(0,0,0,0.7)'; ctx.shadowBlur = 50; ctx.shadowOffsetY = 20;
    ctx.beginPath();
    ctx.moveTo(-250, 130); ctx.lineTo(-250, -10); ctx.lineTo(0, -100); ctx.lineTo(250, -10); ctx.lineTo(250, 130);
    ctx.closePath();
    const wg = ctx.createLinearGradient(0, -100, 0, 130);
    wg.addColorStop(0, '#1a2030'); wg.addColorStop(1, '#0a0d15');
    ctx.fillStyle = wg; ctx.fill();
    ctx.shadowColor = 'transparent'; ctx.shadowBlur = 0; ctx.shadowOffsetY = 0;
    ctx.strokeStyle = 'rgba(255,207,92,0.35)'; ctx.lineWidth = 3; ctx.stroke();
    ctx.fillStyle = '#05070c';
    rr(ctx, -40, 40, 80, 90, 4); ctx.fill();
    ctx.fillStyle = 'rgba(255,207,92,0.06)';
    ctx.strokeStyle = 'rgba(255,207,92,0.2)';
    rr(ctx, -200, 30, 90, 60, 3); ctx.fill(); ctx.stroke();
    rr(ctx, 110, 30, 90, 60, 3); ctx.fill(); ctx.stroke();
    // spotlight sway
    ctx.save();
    ctx.rotate(Math.sin(L * 1.2) * 0.22);
    const sg = ctx.createLinearGradient(0, -100, 0, 260);
    sg.addColorStop(0, 'rgba(255,230,160,0.10)');
    sg.addColorStop(1, 'rgba(255,230,160,0)');
    ctx.fillStyle = sg;
    ctx.beginPath();
    ctx.moveTo(0, -100); ctx.lineTo(-130, 260); ctx.lineTo(130, 260);
    ctx.closePath(); ctx.fill();
    ctx.restore();
    ctx.restore();
  }

  // pin drop
  if (L > aIndustrial - 0.4) {
    const p = clamp01(beat(L, aIndustrial - 0.4, 0.55));
    const bounce = p < 1 ? Math.abs(Math.sin(p * Math.PI * 2.5)) * (1 - p) : Math.abs(Math.sin(L * 2.4)) * 5;
    ctx.save();
    ctx.translate(1150, 375 - 140 * (1 - p) - bounce * 40);
    ctx.globalAlpha = clamp01(p * 2);
    ctx.shadowColor = 'rgba(255,70,70,0.6)'; ctx.shadowBlur = 24;
    ctx.beginPath(); ctx.arc(0, -16, 22, 0, Math.PI * 2);
    ctx.fillStyle = '#ff4646'; ctx.fill();
    ctx.beginPath();
    ctx.moveTo(-14, -4); ctx.lineTo(0, 26); ctx.lineTo(14, -4);
    ctx.closePath(); ctx.fill();
    ctx.beginPath(); ctx.arc(0, -16, 8, 0, Math.PI * 2);
    ctx.fillStyle = '#7a0f18'; ctx.fill();
    ctx.restore();
  }

  // red flags
  if (L > aRaccoon - 1.2) {
    for (let i = 0; i < 3; i++) {
      ctx.save();
      ctx.translate(1290 + i * 44, 330 - i * 16);
      ctx.rotate(Math.sin(L * 5 + i * 1.3) * 0.18);
      ctx.strokeStyle = '#c9d3ef'; ctx.lineWidth = 4;
      ctx.beginPath(); ctx.moveTo(0, 0); ctx.lineTo(0, 54); ctx.stroke();
      ctx.fillStyle = '#ff4646';
      ctx.beginPath();
      ctx.moveTo(0, 0); ctx.lineTo(44 + Math.sin(L * 6 + i) * 5, 8); ctx.lineTo(0, 22);
      ctx.closePath(); ctx.fill();
      ctx.restore();
    }
  }

  // radar magnifier
  if (L > aMap - 0.3) {
    const p = easeOutBack(beat(L, aMap - 0.3, 0.5));
    ctx.save();
    ctx.translate(1370, 190);
    ctx.scale(p, p);
    ctx.beginPath(); ctx.arc(0, 0, 92, 0, Math.PI * 2);
    ctx.fillStyle = 'rgba(255,207,92,0.05)'; ctx.fill();
    ctx.strokeStyle = 'rgba(255,207,92,0.6)'; ctx.lineWidth = 4; ctx.stroke();
    ctx.save();
    ctx.beginPath(); ctx.arc(0, 0, 88, 0, Math.PI * 2); ctx.clip();
    ctx.rotate(L * 2.4);
    const sw = ctx.createConicGradient ? null : null;
    for (let i = 0; i < 20; i++) {
      ctx.fillStyle = `rgba(255,207,92,${0.3 * (1 - i / 20)})`;
      ctx.beginPath();
      ctx.moveTo(0, 0);
      ctx.arc(0, 0, 92, -i * 0.05, -i * 0.05 + 0.05);
      ctx.closePath(); ctx.fill();
    }
    ctx.restore();
    ctx.beginPath(); ctx.arc(10, -12, 7, 0, Math.PI * 2);
    ctx.fillStyle = '#ff4646';
    ctx.shadowColor = '#ff4646'; ctx.shadowBlur = 16;
    ctx.globalAlpha *= 0.5 + 0.5 * Math.sin(L * 6);
    ctx.fill();
    ctx.restore();
    // magnifier handle
    txt(ctx, 'SCAN', 1370, 320, { size: 15, family: 'JBMB', color: 'rgba(255,207,92,0.7)', alpha: p });
  }

  // address card
  if (L > aSuite - 1.2) {
    const p = easeOut(beat(L, aSuite - 1.2, 0.5));
    ctx.save();
    ctx.globalAlpha = p;
    panel(ctx, 100, 140, 480, 170, { r: 16, fill: 'rgba(4,6,10,0.85)', border: 'rgba(255,207,92,0.3)' });
    txt(ctx, 'SHIPPING ADDRESS', 132, 178, { size: 13, family: 'JBMB', color: '#ffcf5c', align: 'left' });
    const tw = typed('9 REBAR YARD, INDUSTRIAL EDGE', A(6, 'industrial'), 1.2, L);
    txt(ctx, tw.s, 132, 216, { size: 20, family: 'JBM', color: '#dfe6ff', align: 'left' });
    if (L > aSuite) txt(ctx, 'NO SUITE NUMBER.', 132, 252, { size: 17, family: 'JBMB', color: '#ff5c5c', align: 'left' });
    if (L > aSuite + 0.7) txt(ctx, 'NO BUSINESS NAME.', 132, 282, { size: 17, family: 'JBMB', color: '#ff5c5c', align: 'left' });
    ctx.restore();
  }

  // abandoned dripping text
  if (L > aWarehouse - 0.2) {
    const p = beat(L, aWarehouse - 0.2, 0.4);
    ctx.save();
    ctx.globalAlpha = p;
    const word2 = 'abandoned…';
    ctx.font = `400 88px AB`;
    let tw2 = 0;
    for (const ch of word2) tw2 += ctx.measureText(ch).width + 4;
    let x = W / 2 - tw2 / 2;
    ctx.textAlign = 'left';
    for (let i = 0; i < word2.length; i++) {
      const ch = word2[i];
      ctx.save();
      ctx.translate(x, 640 + Math.sin(L * 3 + i) * 3);
      ctx.rotate((hash(i) - 0.5) * 0.14);
      ctx.shadowColor = 'rgba(92,214,146,0.5)'; ctx.shadowBlur = 34;
      ctx.fillStyle = i % 2 ? '#9fe8b8' : '#5cd692';
      ctx.fillText(ch, 0, 0);
      ctx.shadowColor = 'transparent';
      if (i % 3 === 0) {
        const dp = (L * 0.7 + hash(i)) % 1;
        ctx.globalAlpha = p * (1 - dp);
        ctx.beginPath(); ctx.arc(10, 22 + dp * 46, 4 + dp * 2, 0, Math.PI * 2);
        ctx.fillStyle = '#5cd692'; ctx.fill();
        ctx.globalAlpha = p;
      }
      ctx.restore();
      x += ctx.measureText(ch).width + 4;
    }
    ctx.restore();
  }

  // raccoon peeking
  if (L > aRaccoon - 0.2) {
    const p = beat(L, aRaccoon - 0.2, 0.3);
    const peek = Math.max(0, Math.sin((L - aRaccoon) * 1.4)) * 70;
    ctx.save();
    ctx.translate(1450, 900 - peek);
    ctx.globalAlpha = p;
    // ears
    ctx.fillStyle = '#6b6f7c';
    ctx.beginPath(); ctx.moveTo(-52, -78); ctx.lineTo(-30, -118); ctx.lineTo(-14, -80); ctx.closePath(); ctx.fill();
    ctx.beginPath(); ctx.moveTo(52, -78); ctx.lineTo(30, -118); ctx.lineTo(14, -80); ctx.closePath(); ctx.fill();
    // head
    ctx.beginPath(); ctx.arc(0, -60, 56, 0, Math.PI * 2);
    ctx.fillStyle = '#8b8f9c'; ctx.fill();
    // mask
    ctx.fillStyle = '#3a3d47';
    ctx.beginPath(); ctx.ellipse(-22, -68, 20, 13, -0.3, 0, Math.PI * 2); ctx.fill();
    ctx.beginPath(); ctx.ellipse(22, -68, 20, 13, 0.3, 0, Math.PI * 2); ctx.fill();
    // eyes
    ctx.fillStyle = '#ffd35c';
    ctx.beginPath(); ctx.arc(-22, -68, 6, 0, Math.PI * 2); ctx.fill();
    ctx.beginPath(); ctx.arc(22, -68, 6, 0, Math.PI * 2); ctx.fill();
    // snout
    ctx.fillStyle = '#e8e9ee';
    ctx.beginPath(); ctx.ellipse(0, -38, 20, 14, 0, 0, Math.PI * 2); ctx.fill();
    ctx.fillStyle = '#26282f';
    ctx.beginPath(); ctx.arc(0, -42, 5, 0, Math.PI * 2); ctx.fill();
    // top hat
    ctx.fillStyle = '#181a22';
    rr(ctx, -34, -178, 68, 62, 6); ctx.fill();
    rr(ctx, -52, -120, 104, 12, 6); ctx.fill();
    ctx.fillStyle = '#ff4646';
    rr(ctx, -34, -132, 68, 10, 2); ctx.fill();
    ctx.restore();
  }
  ctx.restore();

  if (crumple > 0) {
    ctx.fillStyle = `rgba(0,0,0,${crumple * 0.5})`;
    ctx.fillRect(0, 0, W, H);
  }
}

// ---------------------------------------------------------------- SCENE 07
export function s07(ctx, L, t) {
  const end = 19.8;
  const merge = clamp01((L - (end - 0.9)) / 0.9);
  const aPoss = A(7, 'possibilities');
  const aOne = A(7, 'one');
  const aScammed = A(7, 'scammed');
  const aThree = A(7, 'three');

  // paper bg
  const g = ctx.createLinearGradient(0, 0, 0, H);
  g.addColorStop(0, '#f7f3ea'); g.addColorStop(1, '#e6dfcd');
  ctx.fillStyle = g; ctx.fillRect(0, 0, W, H);

  const circles = [
    { at: aPoss + 0.2, color: '#ffd35c', dark: '#7a5a00', label: '1. MYSTERIOUS BILLIONAIRE', sub: 'loves planners?', draw: 'coin' },
    { at: aOne + 0.1, color: '#ff4646', dark: '#7a0f18', label: '2. SPECTACULARLY SCAMMED', sub: 'trap door', draw: 'trap' },
    { at: aScammed + 0.9, color: '#8f7bff', dark: '#372a7a', label: '3. RACCOON BILLIONAIRE', sub: 'top hat & monocle', draw: 'coon' },
  ];

  // connectors
  circles.forEach((c, i) => {
    const p = beat(L, c.at - 0.3, 0.5);
    if (p <= 0) return;
    ctx.save();
    ctx.globalAlpha = p * 0.65;
    ctx.strokeStyle = c.color;
    ctx.lineWidth = 3;
    ctx.setLineDash([10, 8]);
    ctx.lineDashOffset = -L * 40;
    ctx.beginPath();
    ctx.moveTo(800, 240);
    ctx.bezierCurveTo(700 - i * 40, 320, 380 + i * 420, 240, 380 + i * 420, 420);
    ctx.stroke();
    ctx.restore();
  });

  txt(ctx, 'only TWO possibilities → fine, THREE', W / 2, 110, {
    size: 44, family: 'AB', color: '#23262e',
    alpha: beat(L, aPoss, 0.4), scale: 0.85 + 0.15 * easeOutBack(beat(L, aPoss, 0.5)),
  });

  circles.forEach((c, i) => {
    const p = easeOutBack(beat(L, c.at, 0.55));
    if (p <= 0) return;
    const cx = 380 + i * 420;
    const shake = i === 1 && L > aScammed && L < aScammed + 0.8;
    ctx.save();
    ctx.translate(cx + (shake ? (hash(Math.floor(L * 80)) - 0.5) * 12 : 0), 560);
    ctx.scale(p, p);
    ctx.rotate((hash(i) - 0.5) * 0.1 * p);
    // circle
    ctx.beginPath(); ctx.arc(0, -60, 130, 0, Math.PI * 2);
    ctx.fillStyle = rgba(c.color, 0.2); ctx.fill();
    ctx.lineWidth = 4; ctx.strokeStyle = c.color; ctx.stroke();
    // icon
    if (c.draw === 'coin') {
      ctx.beginPath(); ctx.arc(0, -60, 52, 0, Math.PI * 2);
      ctx.fillStyle = '#ffd35c'; ctx.fill();
      ctx.strokeStyle = '#b8860b'; ctx.lineWidth = 5; ctx.stroke();
      txt(ctx, '$', 0, -38, { size: 62, family: 'AB', color: '#7a5a00' });
      for (let k = 0; k < 3; k++) {
        ctx.beginPath(); ctx.arc(52 + k * 14, -18 + k * 10, 12 - k * 2, 0, Math.PI * 2);
        ctx.fillStyle = rgba('#ffd35c', 0.7 - k * 0.2); ctx.fill();
      }
    } else if (c.draw === 'trap') {
      ctx.beginPath(); ctx.ellipse(0, -52, 54, 20, 0, 0, Math.PI * 2);
      ctx.fillStyle = '#1a1a22'; ctx.fill();
      ctx.strokeStyle = '#ff4646'; ctx.lineWidth = 6; ctx.lineCap = 'round';
      ctx.beginPath(); ctx.moveTo(-30, -100); ctx.lineTo(30, -34); ctx.stroke();
      ctx.beginPath(); ctx.moveTo(30, -100); ctx.lineTo(-30, -34); ctx.stroke();
    } else {
      ctx.beginPath(); ctx.arc(0, -50, 42, 0, Math.PI * 2);
      ctx.fillStyle = '#8b8f9c'; ctx.fill();
      ctx.fillStyle = '#3a3d47';
      ctx.beginPath(); ctx.ellipse(-16, -56, 15, 9, -0.3, 0, Math.PI * 2); ctx.fill();
      ctx.beginPath(); ctx.ellipse(16, -56, 15, 9, 0.3, 0, Math.PI * 2); ctx.fill();
      ctx.fillStyle = '#ffd35c';
      ctx.beginPath(); ctx.arc(-16, -56, 4.5, 0, Math.PI * 2); ctx.fill();
      ctx.beginPath(); ctx.arc(16, -56, 4.5, 0, Math.PI * 2); ctx.fill();
      // monocle + top hat
      ctx.strokeStyle = '#d9b64a'; ctx.lineWidth = 3;
      ctx.beginPath(); ctx.arc(16, -56, 13, 0, Math.PI * 2); ctx.stroke();
      ctx.beginPath(); ctx.moveTo(24, -46); ctx.lineTo(34, -10); ctx.stroke();
      ctx.fillStyle = '#181a22';
      rr(ctx, -26, -128, 52, 42, 4); ctx.fill();
      rr(ctx, -38, -90, 76, 9, 4); ctx.fill();
    }
    txt(ctx, c.label, 0, 116, { size: 23, family: 'AB', color: c.dark });
    txt(ctx, c.sub, 0, 152, { size: 27, family: 'CVB', color: '#666' });
    if (i === 2) {
      '   '.split('').forEach((_, k) => {
        const pp = beat(L, aScammed + 1.1 + k * 0.18, 0.3);
        if (pp <= 0) return;
        ctx.save();
        ctx.globalAlpha = pp;
        ctx.translate(-60 + k * 60, 196);
        ctx.rotate(k * 0.24);
        ctx.beginPath(); ctx.ellipse(0, 0, 11, 14, 0, 0, Math.PI * 2);
        ctx.fillStyle = 'rgba(90,70,50,0.75)'; ctx.fill();
        for (let toe = 0; toe < 3; toe++) {
          ctx.beginPath();
          ctx.arc(-9 + toe * 9, -18, 4.5, 0, Math.PI * 2);
          ctx.fill();
        }
        ctx.restore();
      });
    }
    ctx.restore();
  });

  // merge to envelope
  if (merge > 0) {
    ctx.save();
    ctx.translate(W / 2, H * 0.44);
    ctx.scale(merge * 2.2, merge * 2.2);
    ctx.globalAlpha = merge;
    ctx.fillStyle = '#8f7bff';
    ctx.shadowColor = 'rgba(143,123,255,0.8)'; ctx.shadowBlur = 50;
    rr(ctx, -46, -32, 92, 64, 8); ctx.fill();
    ctx.shadowColor = 'transparent';
    ctx.strokeStyle = '#fff'; ctx.lineWidth = 4;
    ctx.beginPath();
    ctx.moveTo(-46, -32); ctx.lineTo(0, 8); ctx.lineTo(46, -32);
    ctx.stroke();
    ctx.restore();
  }
}

// ---------------------------------------------------------------- SCENE 08
export function s08(ctx, L, t) {
  const end = 26.4;
  const glitch = Math.max(0, (L - (end - 0.8)) / 0.8);
  const aEmail = A(8, 'email');
  const aFivemin = A(8, 'fivemin');
  const aReply = A(8, 'reply');
  const aTracking = A(8, 'tracking');

  // inbox bg
  const g = ctx.createLinearGradient(0, 0, W, H);
  g.addColorStop(0, '#0d1424'); g.addColorStop(1, '#070a12');
  ctx.fillStyle = g; ctx.fillRect(0, 0, W, H);

  // floating mail
  for (let i = 0; i < 6; i++) {
    const x = 100 + i * 260 + Math.sin(L * 0.8 + i * 2) * 30;
    const y = 90 + hash(i + 2) * 80 + Math.sin(L * 1.2 + i) * 14;
    ctx.save();
    ctx.globalAlpha = 0.15 + 0.08 * Math.sin(L * 2 + i);
    ctx.translate(x, y);
    ctx.rotate(Math.sin(L + i) * 0.2);
    ctx.strokeStyle = '#5c8bff'; ctx.lineWidth = 2.5;
    rr(ctx, -20, -14, 40, 28, 5); ctx.stroke();
    ctx.beginPath(); ctx.moveTo(-20, -12); ctx.lineTo(0, 4); ctx.lineTo(20, -12); ctx.stroke();
    ctx.restore();
  }

  txt(ctx, 'I email the customer.', W / 2, 84, {
    size: 38, family: 'AB', color: '#a7c1ff', glow: 'rgba(92,139,255,0.5)',
  });

  // window
  const wPop = easeOutBack(beat(L, 0.2, 0.5));
  ctx.save();
  ctx.globalAlpha = wPop;
  panel(ctx, 110, 130, 1380, 560, { r: 22, fill: 'rgba(8,11,20,0.88)', border: 'rgba(92,139,255,0.2)', shadowBlur: 60 });
  txt(ctx, 'Inbox — elliot graye thread', 150, 182, { size: 26, family: 'AB', color: '#dfe6ff', align: 'left' });
  // typing dots
  for (let i = 0; i < 3; i++) {
    const p = Math.sin(L * 5.5 - i * 0.6);
    ctx.beginPath();
    ctx.arc(1420 + i * 0 - 90 + i * 22, 175 - Math.max(0, p) * 7, 5.5, 0, Math.PI * 2);
    ctx.fillStyle = `rgba(92,139,255,${0.4 + 0.6 * Math.max(0, p)})`;
    ctx.fill();
  }

  // outgoing
  const oP = easeOut(beat(L, aEmail - 0.2, 0.5));
  if (oP > 0) {
    ctx.save();
    ctx.globalAlpha = oP;
    ctx.translate(lerp(260, 0, oP), 0);
    panel(ctx, 230, 230, 1020, 130, { r: 16, fill: 'rgba(10,16,28,0.9)', border: 'rgba(0,255,136,0.3)', shadow: false });
    txt(ctx, 'to: elliot graye · 2:11 AM', 260, 262, { size: 13.5, family: 'JBM', color: '#9fb3d9', align: 'left' });
    const ty = typed('Hey Elliot! Huge thanks for your order — just confirming delivery details for such a large shipment.', aEmail + 0.3, 2.2, L);
    ctx.font = `400 19px JBM`; ctx.fillStyle = '#e8ecff'; ctx.textAlign = 'left';
    wrapText(ctx, ty.s + (ty.done ? '' : '▌'), 260, 296, 950, 28);
    ctx.restore();
  }

  // 5 min later
  if (L > aFivemin - 0.6) {
    const p = beat(L, aFivemin - 0.6, 0.4);
    ctx.save();
    ctx.globalAlpha = p;
    ctx.fillStyle = 'rgba(255,215,106,0.1)';
    rr(ctx, W / 2 - 130, 384, 260, 40, 20); ctx.fill();
    ctx.strokeStyle = 'rgba(255,215,106,0.4)'; ctx.lineWidth = 1.5;
    rr(ctx, W / 2 - 130, 384, 260, 40, 20); ctx.stroke();
    txt(ctx, '5 MINUTES LATER', W / 2, 410, { size: 14, family: 'JBMB', color: '#ffd76a' });
    ctx.restore();
  }

  // reply 1
  const r1 = easeOut(beat(L, aFivemin - 0.1, 0.45));
  if (r1 > 0) {
    ctx.save();
    ctx.globalAlpha = r1;
    ctx.translate(lerp(-300, 0, r1), 0);
    panel(ctx, 150, 448, 1000, 116, { r: 16, fill: 'rgba(30,8,12,0.7)', border: 'rgba(255,70,70,0.45)', shadow: false });
    txt(ctx, 'from: elliot graye · received · now', 180, 480, { size: 13.5, family: 'JBM', color: '#ff9db1', align: 'left' });
    txt(ctx, '“Ship ASAP. Need by Friday.', 180, 516, { size: 22, family: 'SGB', color: '#ffe3e9', align: 'left' });
    txt(ctx, 'Don\u2019t call. Busy.”', 180, 546, { size: 22, family: 'SGB', color: '#ff4646', align: 'left' });
    // urgent badge
    const ua = 0.7 + 0.3 * Math.sin(L * 5);
    ctx.fillStyle = `rgba(255,70,70,${ua})`;
    rr(ctx, 1040, 434, 96, 30, 8); ctx.fill();
    txt(ctx, 'URGENT', 1088, 455, { size: 13, family: 'AB', color: '#fff' });
    ctx.restore();
  }

  // reply 2
  if (L > aTracking - 0.9) {
    const r2 = easeOut(beat(L, aTracking - 0.9, 0.45));
    ctx.save();
    ctx.globalAlpha = r2;
    ctx.translate(lerp(-320, 0, r2), 0);
    panel(ctx, 150, 586, 1000, 84, { r: 16, fill: 'rgba(40,4,10,0.8)', border: 'rgba(255,70,70,0.7)', shadow: false });
    ctx.save();
    ctx.translate(180, 636);
    ctx.scale(1 + 0.04 * Math.sin(L * 7), 1 + 0.04 * Math.sin(L * 7));
    txt(ctx, '“Also send tracking immediately.”', 0, 0, {
      size: 24, family: 'AB', color: '#ff5c5c', glow: 'rgba(255,70,70,0.6)', align: 'left',
    });
    ctx.restore();
    ctx.restore();
  }
  ctx.restore();

  // glitch
  if (glitch > 0) {
    for (let i = 0; i < 8; i++) {
      ctx.fillStyle = i % 2 ? 'rgba(92,139,255,0.2)' : 'rgba(255,70,70,0.16)';
      ctx.fillRect((hash(i + 8) - 0.5) * 220 * glitch, hash(i + 4) * H, W, 8 + hash(i) * 26);
    }
  }
}

// ---------------------------------------------------------------- SCENE 09
export function s09(ctx, L, t) {
  const end = 11.9;
  const snap = clamp01((L - (end - 1.1)) / 1.1);
  const fall = snap * snap;
  const aBrain = A(9, 'brain');
  const aCharge = A(9, 'chargebacks');
  const aDelivered = A(9, 'delivered');
  const aNever = A(9, 'never');

  ctx.save();
  ctx.translate(0, fall * 430);
  ctx.scale(1, 1 - fall * 0.85);

  // cork board
  const g = ctx.createRadialGradient(W / 2, 0, 100, W / 2, H / 2, H);
  g.addColorStop(0, '#a06a3c'); g.addColorStop(0.55, '#6d4423'); g.addColorStop(1, '#4a2c14');
  ctx.fillStyle = g; ctx.fillRect(0, -500, W, H + 500);
  for (let i = 0; i < 60; i++) {
    ctx.beginPath();
    ctx.arc(hash(i) * W, hash(i + 30) * H, 1.5 + hash(i + 3) * 2, 0, Math.PI * 2);
    ctx.fillStyle = `rgba(60,34,12,${0.2 + hash(i + 9) * 0.3})`;
    ctx.fill();
  }
  ctx.strokeStyle = 'rgba(20,8,0,0.6)'; ctx.lineWidth = 60;
  ctx.strokeRect(-30, -530, W + 60, H + 560);

  txt(ctx, 'every horror story I\u2019ve ever read:', W / 2, 92, {
    size: 42, family: 'AB', color: '#ffe9c9', glow: 'rgba(0,0,0,0.5)',
    alpha: beat(L, aBrain + 0.6, 0.4),
  });

  // red string
  const pins = [[360, 420], [800, 400], [1240, 380]];
  const strProg = clamp01((L - aCharge + 0.4) / 2.4);
  if (strProg > 0) {
    ctx.save();
    ctx.strokeStyle = '#ff2b2b';
    ctx.lineWidth = 3.4;
    ctx.shadowColor = 'rgba(255,43,43,0.7)'; ctx.shadowBlur = 8;
    const segs = 60;
    ctx.beginPath();
    for (let i = 0; i <= segs * strProg; i++) {
      const p = i / segs;
      const pt = cubicAt(360, 420, 560, 260, 760, 560, 800, 400, p);
      i === 0 ? ctx.moveTo(pt[0], pt[1]) : ctx.lineTo(pt[0], pt[1]);
    }
    if (strProg > 0.5) {
      ctx.bezierCurveTo(850, 220, 1080, 540, 1240, 380);
    }
    ctx.stroke();
    pins.forEach((p, i) => {
      if (strProg > i * 0.3) {
        ctx.beginPath(); ctx.arc(p[0], p[1], 9, 0, Math.PI * 2);
        ctx.fillStyle = '#ff2b2b'; ctx.fill();
      }
    });
    ctx.restore();
  }

  // polaroids
  const pol = [
    { at: aCharge - 0.3, icon: 'card', label: 'CHARGEBACK', sub: 'card + X', rot: -0.12 },
    { at: aCharge + 0.55, icon: 'bolt', label: 'FAKE CARD', sub: 'glitching', rot: 0.07 },
    { at: aCharge + 1.4, icon: 'scale', label: 'DISPUTE', sub: '“delivered” (it was not)', rot: -0.05 },
  ];
  pol.forEach((p2, i) => {
    const pin = easeOutBack(beat(L, p2.at, 0.45));
    if (pin <= 0) return;
    ctx.save();
    ctx.translate(390 + i * 420, 470 + (i % 2) * 90);
    ctx.rotate(p2.rot + Math.sin(L * 1.4 + i) * 0.035);
    ctx.scale(0.5 + 0.5 * pin, 0.5 + 0.5 * pin);
    ctx.globalAlpha = clamp01(pin * 1.5);
    ctx.translate(0, (1 - pin) * -60);
    // pin
    ctx.beginPath(); ctx.arc(0, -14, 9, 0, Math.PI * 2);
    ctx.fillStyle = '#ff2b2b'; ctx.fill();
    // frame
    ctx.shadowColor = 'rgba(30,10,0,0.5)'; ctx.shadowBlur = 30; ctx.shadowOffsetY = 14;
    rr(ctx, -140, -8, 280, 250, 8);
    ctx.fillStyle = '#fdf8ee'; ctx.fill();
    ctx.shadowColor = 'transparent'; ctx.shadowBlur = 0; ctx.shadowOffsetY = 0;
    // art
    ctx.fillStyle = '#22160a';
    if (p2.icon === 'card') {
      rr(ctx, -55, 40, 110, 70, 8); ctx.fill();
      ctx.strokeStyle = '#d92b3a'; ctx.lineWidth = 6; ctx.lineCap = 'round';
      ctx.beginPath(); ctx.moveTo(-40, 50); ctx.lineTo(40, 104); ctx.stroke();
      ctx.beginPath(); ctx.moveTo(40, 50); ctx.lineTo(-40, 104); ctx.stroke();
    } else if (p2.icon === 'bolt') {
      ctx.beginPath();
      ctx.moveTo(6, 24); ctx.lineTo(-26, 84); ctx.lineTo(-2, 84); ctx.lineTo(-10, 134); ctx.lineTo(28, 70); ctx.lineTo(2, 70); ctx.lineTo(20, 24);
      ctx.closePath();
      ctx.fillStyle = hash(Math.floor(L * 14)) > 0.5 ? '#e6b400' : '#d92b3a';
      ctx.fill();
    } else {
      ctx.strokeStyle = '#22160a'; ctx.lineWidth = 6;
      ctx.beginPath(); ctx.moveTo(-40, 116); ctx.lineTo(40, 116); ctx.stroke();
      ctx.beginPath(); ctx.moveTo(0, 116); ctx.lineTo(0, 60); ctx.stroke();
      ctx.beginPath(); ctx.moveTo(-14, 60); ctx.lineTo(44, 60); ctx.stroke();
      ctx.beginPath(); ctx.arc(-24, 44, 12, 0, Math.PI * 2); ctx.fillStyle = '#22160a'; ctx.fill();
      ctx.beginPath(); ctx.arc(56, 34, 16, 0, Math.PI * 2); ctx.fill();
    }
    txt(ctx, p2.label, 0, 172, { size: 20, family: 'AB', color: '#31210f' });
    txt(ctx, p2.sub, 0, 206, { size: 26, family: 'CVB', color: '#6b5232' });
    ctx.restore();
  });

  // newspaper clippings
  if (L > aDelivered - 0.5) {
    ['FAKE CARDS ON THE RISE', '“DELIVERED” DISPUTES DOUBLE', 'SELLER BEWARE'].forEach((h2, i) => {
      const p = easeOut(beat(L, aDelivered - 0.4 + i * 0.5, 0.5));
      if (p <= 0) return;
      ctx.save();
      ctx.globalAlpha = p * 0.96;
      ctx.translate(1150 + i * 24 + Math.sin(L * 1.1 + i * 2) * 6, 700 + i * 46);
      ctx.rotate((hash(i) - 0.5) * 0.16);
      ctx.shadowColor = 'rgba(30,10,0,0.45)'; ctx.shadowBlur = 20; ctx.shadowOffsetY = 8;
      const w2 = measure(ctx, h2, { size: 17, family: 'AB' }) + 44;
      rr(ctx, -w2 / 2, -18, w2, 40, 4);
      ctx.fillStyle = '#f1ead8'; ctx.fill();
      ctx.shadowColor = 'transparent'; ctx.shadowBlur = 0; ctx.shadowOffsetY = 0;
      txt(ctx, h2, 0, 8, { size: 17, family: 'AB', color: '#2a2118' });
      ctx.restore();
    });
  }

  // fake review card
  if (L > aNever) {
    const p = beat(L, aNever, 0.4);
    ctx.save();
    ctx.globalAlpha = p;
    ctx.translate(W / 2, 806);
    ctx.rotate(-0.024);
    panel(ctx, -290, -38, 580, 66, { r: 14, fill: 'rgba(10,10,14,0.85)', border: '#ff5c5c', glow: 'rgba(255,92,92,0.35)' });
    star(ctx, -250, -4, 14, 6, 5, -0.3);
    ctx.fillStyle = '#ffd35c'; ctx.fill();
    txt(ctx, '1/5 — “I nEvEr ReCeIvEd iT”', 20, 6, { size: 21, family: 'JBM', color: '#ffd9d9' });
    ctx.restore();
  }

  // stress meter
  if (L > aNever - 0.9) {
    const p = beat(L, aNever - 0.9, 0.4);
    ctx.save();
    ctx.globalAlpha = p;
    panel(ctx, 110, 700, 330, 110, { r: 14, fill: 'rgba(8,6,4,0.75)', border: 'rgba(255,92,92,0.4)' });
    txt(ctx, 'STRESS METER', 140, 736, { size: 12.5, family: 'JBMB', color: '#ff9d9d', align: 'left' });
    const fill = clamp01((L - aNever + 0.9) / 1.6);
    rr(ctx, 140, 756, 270, 16, 9);
    ctx.fillStyle = 'rgba(255,255,255,0.1)'; ctx.fill();
    if (fill > 0) {
      rr(ctx, 140, 756, 270 * fill, 16, 9);
      ctx.fillStyle = '#ff4646';
      ctx.shadowColor = 'rgba(255,70,70,0.7)'; ctx.shadowBlur = 14;
      ctx.fill();
      ctx.shadowColor = 'transparent';
    }
    ctx.restore();
  }
  ctx.restore();
}

function cubicAt(x0, y0, x1, y1, x2, y2, x3, y3, p) {
  const u = 1 - p;
  const a = u * u * u, b = 3 * u * u * p, c = 3 * u * p * p, d = p * p * p;
  return [a * x0 + b * x1 + c * x2 + d * x3, a * y0 + b * y1 + c * y2 + d * y3];
}

export function wrapText(ctx, text, x, y, maxW, lh) {
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
  return yy;
}
