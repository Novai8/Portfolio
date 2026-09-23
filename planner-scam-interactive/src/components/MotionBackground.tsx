import { useEffect, useRef } from 'react';
import { PALETTES } from '../lib/animationHelpers';

interface Props {
  sceneIdx: number;
  playing: boolean;
}

interface Blob {
  x: number; y: number; r: number; sx: number; sy: number; phase: number;
}
interface Dot {
  x: number; y: number; z: number; vx: number; vy: number; r: number; tw: number;
}

/**
 * MotionBackground — the ever-moving canvas behind every scene:
 * a palette gradient (per scene, cross-faded), three orbiting aurora blobs,
 * drifting depth particles and a vignette. Runs its own rAF loop at display
 * refresh rate, fully independent of React renders.
 */
export function MotionBackground({ sceneIdx, playing }: Props) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const targetPalette = useRef(PALETTES.midnight);
  const speedRef = useRef(1);

  useEffect(() => {
    targetPalette.current = PALETTES[Object.keys(PALETTES)[sceneIdx] ?? 'midnight'] ?? PALETTES.midnight;
  }, [sceneIdx]);

  useEffect(() => {
    speedRef.current = playing ? 1 : 0.25;
  }, [playing]);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;
    const W = 1600;
    const H = 900;
    let raf = 0;
    let last = performance.now();

    const paletteKeys = Object.keys(PALETTES);
    const blobs: Blob[] = Array.from({ length: 3 }, (_, i) => ({
      x: 300 + i * 480, y: 250 + (i % 2) * 380, r: 380 + i * 120,
      sx: 0.00006 + i * 0.00004, sy: 0.00008 - i * 0.00002, phase: i * 2.1,
    }));
    const dots: Dot[] = Array.from({ length: 80 }, (_, i) => ({
      x: Math.random() * W, y: Math.random() * H,
      z: 0.3 + Math.random() * 0.7,
      vx: (Math.random() - 0.5) * 14, vy: -6 - Math.random() * 18,
      r: 1 + Math.random() * 2.6, tw: Math.random() * Math.PI * 2,
    }));

    const hexToRgb = (hex: string): [number, number, number] => {
      const h = hex.replace('#', '');
      return [parseInt(h.slice(0, 2), 16), parseInt(h.slice(2, 4), 16), parseInt(h.slice(4, 6), 16)];
    };
    const mix = (a: [number, number, number], b: [number, number, number], t: number) =>
      `rgb(${Math.round(a[0] + (b[0] - a[0]) * t)},${Math.round(a[1] + (b[1] - a[1]) * t)},${Math.round(a[2] + (b[2] - a[2]) * t)})`;

    let cur: { a: [number, number, number]; b: [number, number, number]; ac: [number, number, number] } = {
      a: hexToRgb(PALETTES.midnight.a),
      b: hexToRgb(PALETTES.midnight.b),
      ac: hexToRgb(PALETTES.midnight.accent),
    };

    const frame = (now: number) => {
      const dt = Math.min(0.05, (now - last) / 1000);
      last = now;
      const tp = targetPalette.current;
      const ta = hexToRgb(tp.a);
      const tb = hexToRgb(tp.b);
      const tac = hexToRgb(tp.accent);
      const k = 1 - Math.pow(0.002, dt); // smooth palette cross-fade
      cur = {
        a: [cur.a[0] + (ta[0] - cur.a[0]) * k, cur.a[1] + (ta[1] - cur.a[1]) * k, cur.a[2] + (ta[2] - cur.a[2]) * k],
        b: [cur.b[0] + (tb[0] - cur.b[0]) * k, cur.b[1] + (tb[1] - cur.b[1]) * k, cur.b[2] + (tb[2] - cur.b[2]) * k],
        ac: [cur.ac[0] + (tac[0] - cur.ac[0]) * k, cur.ac[1] + (tac[1] - cur.ac[1]) * k, cur.ac[2] + (tac[2] - cur.ac[2]) * k],
      };
      const spd = speedRef.current;
      const t = now;

      // base gradient
      const grad = ctx.createLinearGradient(0, 0, W * 0.25, H);
      grad.addColorStop(0, mix(cur.a, cur.b, 0));
      grad.addColorStop(1, mix(cur.a, cur.b, 1));
      ctx.fillStyle = grad;
      ctx.fillRect(0, 0, W, H);

      // aurora blobs
      ctx.globalCompositeOperation = 'screen';
      blobs.forEach((b, i) => {
        const bx = b.x + Math.sin(t * b.sx * spd + b.phase) * 340;
        const by = b.y + Math.cos(t * b.sy * spd + b.phase * 1.7) * 210;
        const rr = b.r * (1 + Math.sin(t * 0.0002 * spd + i) * 0.12);
        const g = ctx.createRadialGradient(bx, by, 0, bx, by, rr);
        const col = i === 1 ? `rgba(${cur.ac[0]},${cur.ac[1]},${cur.ac[2]},` : `rgba(${cur.a[0]},${cur.a[1]},${cur.a[2]},`;
        g.addColorStop(0, col + '0.16)');
        g.addColorStop(1, col + '0)');
        ctx.fillStyle = g;
        ctx.fillRect(0, 0, W, H);
      });

      // depth particles
      dots.forEach((d) => {
        d.x += d.vx * d.z * dt * spd;
        d.y += d.vy * d.z * dt * spd;
        if (d.y < -12) { d.y = H + 10; d.x = Math.random() * W; }
        if (d.x < -12) d.x = W + 10;
        if (d.x > W + 12) d.x = -10;
        const tw = 0.35 + 0.65 * (0.5 + 0.5 * Math.sin(t * 0.002 * spd + d.tw));
        ctx.beginPath();
        ctx.arc(d.x, d.y, d.r * d.z, 0, Math.PI * 2);
        ctx.fillStyle = `rgba(${cur.ac[0]},${cur.ac[1]},${cur.ac[2]},${(0.05 + 0.22 * tw) * d.z})`;
        ctx.fill();
      });
      ctx.globalCompositeOperation = 'source-over';

      // vignette
      const v = ctx.createRadialGradient(W / 2, H / 2, H * 0.35, W / 2, H / 2, H * 0.85);
      v.addColorStop(0, 'rgba(0,0,0,0)');
      v.addColorStop(1, 'rgba(0,0,0,0.42)');
      ctx.fillStyle = v;
      ctx.fillRect(0, 0, W, H);

      // keep palette key in ref for debugging
      void paletteKeys;
      raf = requestAnimationFrame(frame);
    };
    raf = requestAnimationFrame(frame);
    return () => cancelAnimationFrame(raf);
  }, []);

  return (
    <canvas
      ref={canvasRef}
      width={1600}
      height={900}
      style={{ position: 'absolute', inset: 0, width: '100%', height: '100%' }}
      aria-hidden
    />
  );
}
