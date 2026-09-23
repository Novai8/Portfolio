/**
 * lib.mjs — shared drawing kit for the offline (in-sandbox) renderer.
 * Same 1600×900 design space as the React app; the main loop scales to 1080p.
 */
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import { GlobalFonts } from '@napi-rs/canvas';

export const W = 1600;
export const H = 900;

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../..');

// ---------- fonts ----------
function findFont(pkg, file) {
  const base = path.join(ROOT, 'node_modules', '@expo-google-fonts', pkg);
  const stack = [base];
  while (stack.length) {
    const dir = stack.pop();
    for (const e of fs.readdirSync(dir, { withFileTypes: true })) {
      const p = path.join(dir, e.name);
      if (e.isDirectory()) stack.push(p);
      else if (e.name === file) return p;
    }
  }
  throw new Error(`font not found: ${pkg}/${file}`);
}

export function registerFonts() {
  GlobalFonts.registerFromPath(findFont('archivo-black', 'ArchivoBlack_400Regular.ttf'), 'AB');
  GlobalFonts.registerFromPath(findFont('space-grotesk', 'SpaceGrotesk_400Regular.ttf'), 'SG');
  GlobalFonts.registerFromPath(findFont('space-grotesk', 'SpaceGrotesk_500Medium.ttf'), 'SGM');
  GlobalFonts.registerFromPath(findFont('space-grotesk', 'SpaceGrotesk_700Bold.ttf'), 'SGB');
  GlobalFonts.registerFromPath(findFont('jetbrains-mono', 'JetBrainsMono_400Regular.ttf'), 'JBM');
  GlobalFonts.registerFromPath(findFont('jetbrains-mono', 'JetBrainsMono_700Bold.ttf'), 'JBMB');
  GlobalFonts.registerFromPath(findFont('caveat', 'Caveat_600SemiBold.ttf'), 'CV');
  GlobalFonts.registerFromPath(findFont('caveat', 'Caveat_700Bold.ttf'), 'CVB');
}

// ---------- data ----------
export const DATA = {
  words: JSON.parse(fs.readFileSync(path.join(ROOT, 'src/data/word_timestamps.json'), 'utf8')),
  chunks: JSON.parse(fs.readFileSync(path.join(ROOT, 'src/data/chunks.json'), 'utf8')),
  scenes: JSON.parse(fs.readFileSync(path.join(ROOT, 'src/data/scenes.json'), 'utf8')),
  anchors: JSON.parse(fs.readFileSync(path.join(ROOT, 'src/data/anchors.json'), 'utf8')),
};

export const TOTAL = DATA.words[DATA.words.length - 1].end + 0.02;

export function anchorLocal(sceneId, key) {
  const a = DATA.anchors[String(sceneId)]?.[key];
  const s = DATA.scenes[sceneId - 1];
  return a !== undefined && s ? a - s.start : Number.POSITIVE_INFINITY;
}

// ---------- math ----------
export const clamp01 = (v) => (v < 0 ? 0 : v > 1 ? 1 : v);
export const beat = (local, at, dur = 0.6) => clamp01((local - at) / dur);
export const easeOut = (p) => 1 - Math.pow(1 - clamp01(p), 3);
export const easeOutBack = (p) => {
  const c = 1.7;
  const x = clamp01(p) - 1;
  return 1 + (c + 1) * x * x * x + c * x * x;
};
export const hash = (i) => {
  const x = Math.sin(i * 127.1 + 311.7) * 43758.5453;
  return x - Math.floor(x);
};
export const lerp = (a, b, t) => a + (b - a) * t;

export function hexRgb(hex) {
  const h = hex.replace('#', '');
  return [parseInt(h.slice(0, 2), 16), parseInt(h.slice(2, 4), 16), parseInt(h.slice(4, 6), 16)];
}
export function rgba(hex, a) {
  const [r, g, b] = hexRgb(hex);
  return `rgba(${r},${g},${b},${a})`;
}
export function mixHex(h1, h2, t) {
  const a = hexRgb(h1);
  const b = hexRgb(h2);
  const c = (i) => Math.round(lerp(a[i], b[i], t)).toString(16).padStart(2, '0');
  return `#${c(0)}${c(1)}${c(2)}`;
}

// ---------- palettes (same as the app) ----------
export const PALETTES = [
  { a: '#2b1e5e', b: '#0c1230', accent: '#8f7bff' }, // midnight
  { a: '#ffd9c7', b: '#bff5e0', accent: '#0e9f6e', light: true }, // peachmint
  { a: '#0a0f2e', b: '#05070f', accent: '#00e5ff' }, // neon
  { a: '#2d0a3a', b: '#12042a', accent: '#ff006e' }, // comic
  { a: '#081108', b: '#020603', accent: '#39ff88' }, // monitor
  { a: '#12141c', b: '#07080d', accent: '#ffcf5c' }, // mapnoir
  { a: '#f5f1e8', b: '#e0d8c4', accent: '#d92b3a', light: true }, // paperwhite
  { a: '#101625', b: '#090c14', accent: '#5c8bff' }, // inbox
  { a: '#8a5a33', b: '#4a2c14', accent: '#ffd35c' }, // cork
  { a: '#1b2a4a', b: '#0d1426', accent: '#7ad0ff' }, // iso
  { a: '#2a1240', b: '#0e3b2e', accent: '#ff8ac2' }, // callsplit
  { a: '#0d0f16', b: '#050609', accent: '#ffd76a' }, // noirbrowser
  { a: '#33060d', b: '#12020a', accent: '#ff3b5c' }, // redalert
  { a: '#0a1626', b: '#04080f', accent: '#61b0ff' }, // service
  { a: '#1c0505', b: '#080101', accent: '#ff4646' }, // ransom
  { a: '#062033', b: '#02090f', accent: '#00c2ff' }, // techgrid
  { a: '#2a1a4a', b: '#4a2a5e', accent: '#ffd35c' }, // softjoy
  { a: '#ff9a3c', b: '#3a1c5a', accent: '#ffd35c' }, // sunrise
];

// ---------- primitives ----------
export function rr(ctx, x, y, w, h, r) {
  const rad = Math.min(r, w / 2, h / 2);
  ctx.beginPath();
  ctx.moveTo(x + rad, y);
  ctx.arcTo(x + w, y, x + w, y + h, rad);
  ctx.arcTo(x + w, y + h, x, y + h, rad);
  ctx.arcTo(x, y + h, x, y, rad);
  ctx.arcTo(x, y, x + w, y, rad);
  ctx.closePath();
}

/** Rounded panel with shadow/border/glow. */
export function panel(ctx, x, y, w, h, o = {}) {
  const r = o.r ?? 20;
  ctx.save();
  if (o.alpha !== undefined) ctx.globalAlpha *= o.alpha;
  if (o.shadow !== false) {
    ctx.shadowColor = o.shadowColor ?? 'rgba(0,0,0,0.45)';
    ctx.shadowBlur = o.shadowBlur ?? 40;
    ctx.shadowOffsetY = 14;
  }
  if (o.glow) {
    ctx.shadowColor = o.glow;
    ctx.shadowBlur = 50;
  }
  rr(ctx, x, y, w, h, r);
  ctx.fillStyle = o.fill ?? 'rgba(255,255,255,0.06)';
  ctx.fill();
  ctx.shadowColor = 'transparent';
  ctx.shadowBlur = 0;
  ctx.shadowOffsetY = 0;
  if (o.border) {
    ctx.strokeStyle = o.border;
    ctx.lineWidth = o.borderWidth ?? 1.5;
    rr(ctx, x, y, w, h, r);
    ctx.stroke();
  }
  ctx.restore();
}

/** Text with optional glow / rotate / scale / pop-in. */
export function txt(ctx, str, x, y, o = {}) {
  ctx.save();
  const size = o.size ?? 24;
  ctx.font = `${o.style ? o.style + ' ' : ''}${o.weight ?? 400} ${size}px ${o.family ?? 'SG'}`;
  ctx.textAlign = o.align ?? 'center';
  ctx.textBaseline = o.baseline ?? 'alphabetic';
  ctx.globalAlpha *= o.alpha ?? 1;
  if (o.rotate) { ctx.translate(x, y); ctx.rotate(o.rotate); x = 0; y = 0; }
  if (o.scale && o.scale !== 1) {
    ctx.translate(x, y);
    ctx.scale(o.scale, o.scale);
    x = 0; y = 0;
  }
  if (o.glow) {
    ctx.shadowColor = o.glow;
    ctx.shadowBlur = o.glowSize ?? 24;
  }
  ctx.fillStyle = o.color ?? '#fff';
  ctx.fillText(str, x, y);
  ctx.restore();
}

/** Measure with a given font spec without changing state. */
export function measure(ctx, str, o = {}) {
  ctx.save();
  ctx.font = `${o.weight ?? 400} ${o.size ?? 24}px ${o.family ?? 'SG'}`;
  const w = ctx.measureText(str).width;
  ctx.restore();
  return w;
}

export function typed(str, at, dur, local) {
  const p = beat(local, at, dur);
  return { s: str.slice(0, Math.floor(p * str.length)), done: p >= 1, p };
}

/** Simple star polygon path. */
export function star(ctx, cx, cy, ro, ri, points, rot) {
  ctx.beginPath();
  for (let i = 0; i < points * 2; i++) {
    const r = i % 2 === 0 ? ro : ri;
    const a = (i / (points * 2)) * Math.PI * 2 + rot;
    const x = cx + Math.cos(a) * r;
    const y = cy + Math.sin(a) * r;
    i === 0 ? ctx.moveTo(x, y) : ctx.lineTo(x, y);
  }
  ctx.closePath();
}

/** Heart path centered at (x,y), size s ≈ width. */
export function heart(ctx, x, y, s) {
  const r = s * 0.3;
  ctx.beginPath();
  ctx.moveTo(x, y + s * 0.32);
  ctx.bezierCurveTo(x - s * 0.55, y - s * 0.12, x - r, y - s * 0.42, x, y - s * 0.14);
  ctx.bezierCurveTo(x + r, y - s * 0.42, x + s * 0.55, y - s * 0.12, x, y + s * 0.32);
  ctx.closePath();
}

/** Music note (drawn upside down for the "sad hold music" gag). */
export function note(ctx, x, y, s, color, alpha) {
  ctx.save();
  ctx.globalAlpha *= alpha;
  ctx.fillStyle = color;
  ctx.strokeStyle = color;
  ctx.lineWidth = s * 0.16;
  ctx.beginPath();
  ctx.ellipse(x, y, s * 0.24, s * 0.17, -0.4, 0, Math.PI * 2);
  ctx.fill();
  ctx.beginPath();
  ctx.moveTo(x + s * 0.2, y - s * 0.05);
  ctx.lineTo(x + s * 0.2, y - s * 0.85);
  ctx.stroke();
  ctx.beginPath();
  ctx.moveTo(x + s * 0.2, y - s * 0.85);
  ctx.quadraticCurveTo(x + s * 0.55, y - s * 0.7, x + s * 0.52, y - s * 0.4);
  ctx.stroke();
  ctx.restore();
}

// ---------- animated background ----------
let bgSeedDots = null;
function dots() {
  if (!bgSeedDots) {
    bgSeedDots = Array.from({ length: 70 }, (_, i) => ({
      x: hash(i) * W, y: hash(i + 50) * H, z: 0.3 + hash(i + 90) * 0.7,
      vx: (hash(i + 30) - 0.5) * 14, vy: -6 - hash(i + 60) * 18,
      r: 1 + hash(i + 40) * 2.6, tw: hash(i + 70) * Math.PI * 2,
    }));
  }
  return bgSeedDots;
}

/** Global animated background: palette crossfade + blobs + particles + vignette. */
export function drawBackground(ctx, t, sceneIdx) {
  const idx = sceneIdx;
  const prev = Math.max(0, idx - 1);
  const s = DATA.scenes[idx];
  const local = t - s.start;
  const blend = 1 - Math.pow(0.0015, 1 / 60) ** 0; // not time-based; do boundary fade:
  void blend;
  const k = clamp01(local / 0.9); // crossfade from previous palette over 0.9s
  const P = PALETTES[idx];
  const PP = PALETTES[prev];
  const top = mixHex(PP.a, P.a, k);
  const bot = mixHex(PP.b, P.b, k);
  const acc = mixHex(PP.accent, P.accent, k);

  const g = ctx.createLinearGradient(0, 0, W * 0.25, H);
  g.addColorStop(0, top);
  g.addColorStop(1, bot);
  ctx.fillStyle = g;
  ctx.fillRect(0, 0, W, H);

  // three orbiting aurora blobs
  ctx.save();
  ctx.globalCompositeOperation = 'screen';
  for (let i = 0; i < 3; i++) {
    const bx = 300 + i * 480 + Math.sin(t * 0.00006 * 1000 * (0.6 + i * 0.4) + i * 2.1) * 340;
    const by = 250 + (i % 2) * 380 + Math.cos(t * 0.00008 * 1000 * (0.8 + i * 0.3) + i * 1.6) * 210;
    const rad = (380 + i * 120) * (1 + Math.sin(t * 0.0002 * 1000 + i) * 0.12);
    const rg = ctx.createRadialGradient(bx, by, 0, bx, by, rad);
    const col = i === 1 ? acc : top;
    rg.addColorStop(0, rgba(col.startsWith('#') ? col : '#5a5a8f', 0.15));
    rg.addColorStop(1, 'rgba(0,0,0,0)');
    ctx.fillStyle = rg;
    ctx.fillRect(0, 0, W, H);
  }
  ctx.restore();

  // particles
  ctx.save();
  for (const d of dots()) {
    const dt = 1 / 60;
    d.x += d.vx * d.z * dt;
    d.y += d.vy * d.z * dt;
    if (d.y < -12) { d.y = H + 10; d.x = hash(Math.random() * 999) * W; }
    if (d.x < -12) d.x = W + 10;
    if (d.x > W + 12) d.x = -10;
    const tw = 0.35 + 0.65 * (0.5 + 0.5 * Math.sin(t * 2 + d.tw));
    ctx.beginPath();
    ctx.arc(d.x, d.y, d.r * d.z, 0, Math.PI * 2);
    ctx.fillStyle = rgba(acc, (0.05 + 0.22 * tw) * d.z);
    ctx.fill();
  }
  ctx.restore();

  // vignette
  const v = ctx.createRadialGradient(W / 2, H / 2, H * 0.35, W / 2, H / 2, H * 0.85);
  v.addColorStop(0, 'rgba(0,0,0,0)');
  v.addColorStop(1, 'rgba(0,0,0,0.42)');
  ctx.fillStyle = v;
  ctx.fillRect(0, 0, W, H);
}

// ---------- karaoke captions ----------
const captionCache = new Map();
function captionLayout(chunk, ctx) {
  if (captionCache.has(chunk.i)) return captionCache.get(chunk.i);
  const words = DATA.words.slice(chunk.w0, chunk.w1 + 1);
  const size = 30;
  ctx.save();
  ctx.font = `500 ${size}px SGM`;
  const spaceW = ctx.measureText(' ').width;
  const items = words.map((w) => ({ ...w, width: ctx.measureText(w.word).width }));
  ctx.restore();
  const maxW = 1280;
  const lines = [];
  let line = [];
  let lw = 0;
  for (const it of items) {
    const add = line.length ? spaceW + it.width : it.width;
    if (line.length && lw + add > maxW) {
      lines.push({ items: line, width: lw });
      line = [it];
      lw = it.width;
    } else {
      line.push(it);
      lw += add;
    }
  }
  if (line.length) lines.push({ items: line, width: lw });
  // assign global word indices in order
  let gi = chunk.w0;
  for (const l of lines) for (const it of l.items) it.gi = gi++;
  const layout = { size, spaceW, lines, totalH: lines.length * 44 };
  captionCache.set(chunk.i, layout);
  return layout;
}

export function chunkAt(t) {
  const cs = DATA.chunks;
  let lo = 0;
  let hi = cs.length - 1;
  while (lo <= hi) {
    const mid = (lo + hi) >> 1;
    const c = cs[mid];
    if (t < c.start - 0.1) hi = mid - 1;
    else if (t > c.end + 0.45) lo = mid + 1;
    else return c;
  }
  return null;
}

export function wordIndexAt(t) {
  const ws = DATA.words;
  let lo = 0;
  let hi = ws.length - 1;
  if (t <= ws[0].start) return 0;
  if (t >= ws[hi].start) return hi;
  while (lo <= hi) {
    const mid = (lo + hi) >> 1;
    if (ws[mid].start <= t) {
      if (mid === ws.length - 1 || ws[mid + 1].start > t) return mid;
      lo = mid + 1;
    } else hi = mid - 1;
  }
  return 0;
}

/** Word-synced karaoke captions, bottom center. */
export function drawCaptions(ctx, t) {
  const chunk = chunkAt(t);
  if (!chunk) return;
  const L = captionLayout(chunk, ctx);
  const wordIdx = wordIndexAt(t);
  const cx = W / 2;
  const bottom = 828;
  const pop = easeOutBack(beat(t, chunk.start - 0.05, 0.3));

  ctx.save();
  ctx.translate(cx, bottom);
  ctx.scale(0.96 + 0.04 * pop, 0.96 + 0.04 * pop);
  ctx.translate(-cx, -bottom);

  // panel
  const padX = 34;
  const padY = 22;
  const boxW = Math.max(...L.lines.map((l) => l.width)) + padX * 2;
  const boxH = L.totalH + padY * 2;
  panel(ctx, cx - boxW / 2, bottom - boxH + 26, boxW, boxH, {
    r: 16,
    fill: 'rgba(4,6,16,0.74)',
    border: 'rgba(255,255,255,0.09)',
    shadowBlur: 30,
  });

  ctx.textBaseline = 'middle';
  let y = bottom - L.totalH + 34;
  for (const line of L.lines) {
    let x = cx - line.width / 2;
    for (const it of line.items) {
      const isSpoken = it.i !== undefined ? false : chunk.w0 + line.items.indexOf(it) < 0; // unused
      void isSpoken;
      const gi = it.gi;
      const active = gi === wordIdx;
      const spoken = gi < wordIdx;
      ctx.save();
      ctx.font = `${active ? 700 : 500} ${L.size}px SGM`;
      ctx.textAlign = 'left';
      if (active) {
        ctx.translate(x + it.width / 2, y - 4);
        ctx.scale(1.18, 1.18);
        ctx.translate(-(x + it.width / 2), -(y - 4));
        ctx.shadowColor = 'rgba(0,255,136,0.55)';
        ctx.shadowBlur = 18;
        ctx.fillStyle = '#00ff88';
      } else {
        ctx.fillStyle = spoken ? 'rgba(150,160,189,0.85)' : 'rgba(232,236,255,0.34)';
      }
      ctx.fillText(it.word, x, y);
      ctx.restore();
      x += it.width + L.spaceW;
    }
    y += 44;
  }
  ctx.restore();
}

/** attach global word index once for layout reuse */
export function prepChunks() {
  for (const c of DATA.chunks) {
    const words = DATA.words.slice(c.w0, c.w1 + 1);
    c._words = words;
  }
}

export function captionLayoutWithGi(chunk, ctx) {
  // same as captionLayout but items get gi (call after prepChunks)
  const cached = captionCache.get(chunk.i);
  if (cached && cached.gi) return cached;
  const L = { ...captionLayout(chunk, ctx), gi: true };
  let k = 0;
  for (const line of L.lines) {
    for (const it of line.items) {
      it.gi = chunk.w0 + k;
      // recompute width per word (already measured)
      k++;
    }
  }
  captionCache.set(chunk.i, L);
  return L;
}

/** Scene-start flash + scene label. */
export function sceneStartFlash(ctx, local, sceneIdx) {
  if (sceneIdx === 0) return;
  const p = beat(local, 0, 0.32);
  if (p < 1) {
    ctx.fillStyle = `rgba(255,255,255,${0.4 * (1 - p)})`;
    ctx.fillRect(0, 0, W, H);
  }
}

/** Film grain-ish speckle (cheap: sparse random dots each frame). */
export function grain(ctx, t) {
  ctx.save();
  ctx.globalAlpha = 0.05;
  ctx.fillStyle = '#fff';
  const n = 90;
  for (let i = 0; i < n; i++) {
    const h1 = hash(i * 7.3 + Math.floor(t * 24) * 13.7);
    const h2 = hash(i * 3.1 + Math.floor(t * 24) * 7.9);
    ctx.fillRect(h1 * W, h2 * H, 2, 2);
  }
  ctx.restore();
}
