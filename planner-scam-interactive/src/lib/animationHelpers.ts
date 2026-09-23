/** animationHelpers.ts — small shared math/tween utilities used by scenes. */

export const clamp = (v: number, min = 0, max = 1) => Math.min(max, Math.max(min, v));
export const lerp = (a: number, b: number, t: number) => a + (b - a) * clamp(t);
export const mapRange = (v: number, a0: number, a1: number, b0: number, b1: number) =>
  b0 + (b1 - b0) * clamp((v - a0) / (a1 - a0 || 1));
export const rand = (min: number, max: number) => min + Math.random() * (max - min);
export const pick = <T,>(arr: T[]): T => arr[Math.floor(Math.random() * arr.length)];

/** Progress of a beat that starts `at` seconds into the scene and lasts `dur`. */
export const beat = (local: number, at: number, dur = 0.6) => clamp((local - at) / dur);

/** Sawtooth loop progress (0→1 repeating) for infinite motions. */
export const loop01 = (local: number, period: number, offset = 0) =>
  (((local + offset) % period) + period) % period / period;

/** Ping-pong 0→1→0 loop. */
export const pingpong = (local: number, period: number, offset = 0) => {
  const p = loop01(local, period, offset);
  return p < 0.5 ? p * 2 : (1 - p) * 2;
};

/** Pseudo-random but stable per-index float in [0,1). */
export const hash = (i: number) => {
  const x = Math.sin(i * 127.1 + 311.7) * 43758.5453;
  return x - Math.floor(x);
};

/** n staggered items visible by local time `t`, each popping over `each` seconds. */
export const staggerCount = (t: number, at: number, each: number, n: number) =>
  Math.max(0, Math.min(n, Math.floor((t - at) / each) + 1));

/** seconds→"MM:SS" */
export const mmss = (s: number) =>
  `${Math.floor(Math.max(0, s) / 60)}:${Math.floor(Math.max(0, s) % 60)
    .toString()
    .padStart(2, '0')}`;

export const PALETTES: Record<string, { a: string; b: string; accent: string }> = {
  midnight: { a: '#2b1e5e', b: '#0c1230', accent: '#8f7bff' },
  peachmint: { a: '#ffd9c7', b: '#bff5e0', accent: '#0e9f6e' },
  neon: { a: '#0a0f2e', b: '#05070f', accent: '#00e5ff' },
  comic: { a: '#2d0a3a', b: '#12042a', accent: '#ff006e' },
  monitor: { a: '#081108', b: '#020603', accent: '#39ff88' },
  mapnoir: { a: '#12141c', b: '#07080d', accent: '#ffcf5c' },
  paperwhite: { a: '#f5f1e8', b: '#e8e2d2', accent: '#d92b3a' },
  inbox: { a: '#101625', b: '#090c14', accent: '#5c8bff' },
  cork: { a: '#8a5a33', b: '#5d3a1e', accent: '#ffd35c' },
  iso: { a: '#1b2a4a', b: '#0d1426', accent: '#7ad0ff' },
  callsplit: { a: '#2a1240', b: '#0e3b2e', accent: '#ff8ac2' },
  noirbrowser: { a: '#0d0f16', b: '#050609', accent: '#ffd76a' },
  redalert: { a: '#33060d', b: '#12020a', accent: '#ff3b5c' },
  service: { a: '#0a1626', b: '#04080f', accent: '#61b0ff' },
  ransom: { a: '#1c0505', b: '#080101', accent: '#ff4646' },
  techgrid: { a: '#062033', b: '#02090f', accent: '#00c2ff' },
  softjoy: { a: '#2a1a4a', b: '#4a2a5e', accent: '#ffd35c' },
  sunrise: { a: '#ff9a3c', b: '#3a1c5a', accent: '#ffd35c' },
};
