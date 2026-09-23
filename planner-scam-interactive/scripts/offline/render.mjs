/**
 * render.mjs — offline frame renderer → final.mp4 (+ preview.gif).
 *
 * Renders every frame of the 10:32 experience on a canvas (same 1600×900
 * design space as the React app, scaled to 1920×1080) and streams raw RGBA
 * frames into ffmpeg (from @ffmpeg-installer) together with the voiceover.
 *
 * Usage:
 *   node scripts/offline/render.mjs                    # full render → final.mp4
 *   node scripts/offline/render.mjs --qa               # QA stills → /tmp/qa
 *   node scripts/offline/render.mjs --bench            # speed benchmark
 *   FPS=30 node scripts/offline/render.mjs
 */
import fs from 'fs';
import path from 'path';
import { spawn } from 'child_process';
import { createCanvas } from '@napi-rs/canvas';
import {
  W, H, DATA, TOTAL, registerFonts, drawBackground, drawCaptions,
  sceneStartFlash, grain, wordIndexAt,
} from './lib.mjs';
import { s01, s02, s03, s04, s05, s06, s07, s08, s09 } from './scenes1.mjs';
import { s10, s11, s12, s13, s14, s15, s16, s17, s18, setEnd } from './scenes2.mjs';
import { createRequire } from 'module';

const require = createRequire(import.meta.url);
const ROOT = path.resolve(path.dirname(new URL(import.meta.url).pathname), '../..');
const FF = require('@ffmpeg-installer/ffmpeg').path;
const FFPROBE = require('@ffprobe-installer/ffprobe').path;

const args = process.argv.slice(2);
const QA = args.includes('--qa');
const BENCH = args.includes('--bench');
const FPS = parseInt(process.env.FPS || '30', 10);
const OUT = path.join(ROOT, process.env.OUT || 'final.mp4');

setEnd(TOTAL - 0);

const SCENE_FNS = [s01, s02, s03, s04, s05, s06, s07, s08, s09, s10, s11, s12, s13, s14, s15, s16, s17, s18];

function sceneIndexAt(t) {
  const sc = DATA.scenes;
  for (let i = sc.length - 1; i >= 0; i--) if (t >= sc[i].start) return i;
  return 0;
}

const canvas = createCanvas(1920, 1080);
const ctx = canvas.getContext('2d');

function drawFrame(t) {
  ctx.setTransform(1, 0, 0, 1, 0, 0);
  ctx.clearRect(0, 0, 1920, 1080);
  ctx.setTransform(1.2, 0, 0, 1.2, 0, 0); // 1600×900 → 1920×1080

  const si = sceneIndexAt(t);
  const scene = DATA.scenes[si];
  const L = Math.max(0, t - scene.start);

  drawBackground(ctx, t, si);
  SCENE_FNS[si](ctx, L, t);
  drawCaptions(ctx, t);
  sceneStartFlash(ctx, L, si);
  grain(ctx, t);
}

async function main() {
  registerFonts();
  const duration = TOTAL + 1.2; // hold end card a moment

  if (QA) {
    const outDir = '/tmp/qa';
    fs.mkdirSync(outDir, { recursive: true });
    const times = [2, 5, 20, 33, 45, 52, 70, 95, 110, 125, 140, 150, 165, 180, 200, 215, 240, 260, 275, 300, 320, 350, 380, 400, 430, 460, 480, 500, 520, 540, 560, 580, 600, 620, 631];
    for (const tt of times) {
      drawFrame(tt);
      const buf = await canvas.encode('png');
      fs.writeFileSync(path.join(outDir, `t${String(Math.round(tt)).padStart(4, '0')}.png`), buf);
    }
    console.log('QA stills written to', outDir);
    return;
  }

  if (BENCH) {
    const n = 120;
    const t0 = Date.now();
    for (let i = 0; i < n; i++) drawFrame(100 + i / FPS);
    const per = (Date.now() - t0) / n;
    const total = ((duration * FPS * per) / 1000 / 60).toFixed(1);
    console.log(`bench: ${per.toFixed(1)} ms/frame @30fps → full render ≈ ${total} min`);
    return;
  }

  const totalFrames = Math.round(duration * FPS);
  console.log(`render: ${totalFrames} frames @ ${FPS}fps, duration ${duration.toFixed(2)}s → ${OUT}`);

  const ffArgs = [
    '-y',
    '-f', 'rawvideo', '-pix_fmt', 'rgba', '-s', '1920x1080', '-r', String(FPS), '-i', '-',
    '-i', path.join(ROOT, 'public/assets/audio/voiceover.mp3'),
    '-map', '0:v', '-map', '1:a',
    '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '27',
    '-maxrate', '2400k', '-bufsize', '4800k',
    '-pix_fmt', 'yuv420p',
    '-c:a', 'aac', '-b:a', '128k',
    '-shortest', '-movflags', '+faststart',
    OUT,
  ];
  const ff = spawn(FF, ffArgs, { stdio: ['pipe', 'inherit', 'inherit'] });

  const t0 = Date.now();
  let ffmpegClosed = false;
  ff.on('close', () => { ffmpegClosed = true; });
  ff.stdin.on('error', () => { /* -shortest closes the pipe ~1s before our last frame; safe to stop */ });
  for (let f = 0; f < totalFrames; f++) {
    if (ffmpegClosed) break; // audio ended (with -shortest) → ffmpeg is done
    const t = f / FPS;
    drawFrame(t);
    const { data } = ctx.getImageData(0, 0, 1920, 1080);
    const buf = Buffer.from(data.buffer, data.byteOffset, data.byteLength);
    if (!ff.stdin.write(buf)) {
      await new Promise((res) => ff.stdin.once('drain', res));
    }
    if (f % 300 === 0) {
      const pct = ((f / totalFrames) * 100).toFixed(1);
      const elapsed = (Date.now() - t0) / 1000;
      const eta = elapsed / Math.max(1, f) * (totalFrames - f);
      console.log(`frame ${f}/${totalFrames} (${pct}%) elapsed ${elapsed.toFixed(0)}s eta ${eta.toFixed(0)}s`);
    }
  }
  if (!ffmpegClosed) ff.stdin.end();
  await new Promise((res) => ff.on('close', res));
  console.log('ffmpeg done in', ((Date.now() - t0) / 1000).toFixed(0), 's');

  // size guard: re-encode down if the file is huge
  const size = fs.statSync(OUT).size;
  console.log('final.mp4 size:', (size / 1024 / 1024).toFixed(1), 'MB');
  if (size > 100 * 1024 * 1024) {
    console.log('file > 100 MB — compressing to fit workspace budget…');
    const tmp = OUT + '.tmp.mp4';
    await new Promise((res) => {
      const p2 = spawn(FF, [
        '-y', '-i', OUT, '-c:v', 'libx264', '-preset', 'medium',
        '-b:v', '1000k', '-maxrate', '1400k', '-bufsize', '2800k',
        '-pix_fmt', 'yuv420p', '-c:a', 'copy', '-movflags', '+faststart', tmp,
      ], { stdio: ['ignore', 'inherit', 'inherit'] });
      p2.on('close', res);
    });
    fs.renameSync(tmp, OUT);
    console.log('compressed size:', (fs.statSync(OUT).size / 1024 / 1024).toFixed(1), 'MB');
  }

  // preview.gif (first 10 s)
  console.log('creating preview.gif…');
  await new Promise((res) => {
    const p3 = spawn(FF, [
      '-y', '-i', OUT, '-t', '10',
      '-vf', 'fps=12,scale=640:-1:flags=lanczos,split[s0][s1];[s0]palettegen[p];[s1][p]paletteuse',
      path.join(ROOT, 'preview.gif'),
    ], { stdio: ['ignore', 'inherit', 'inherit'] });
    p3.on('close', res);
  });
  console.log('preview.gif done');

  // verify duration
  const probe = spawn(FFPROBE, ['-v', 'error', '-show_entries', 'format=duration,size', '-of', 'default=noprint_wrappers=1', OUT]);
  probe.stdout.on('data', (d) => process.stdout.write(d));
}

main().catch((e) => {
  console.error(e);
  process.exit(1);
});
