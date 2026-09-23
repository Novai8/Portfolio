/**
 * render-video.js — exports the interactive experience to final.mp4.
 *
 * REQUIREMENTS (not available inside the build sandbox, preinstalled on most
 * dev machines):
 *   1. ffmpeg on PATH          (apt/brew/choco install ffmpeg)
 *   2. a Chromium binary for Puppeteer:
 *        npx @puppeteer/browsers install chrome@stable
 *      or set PUPPETEER_EXECUTABLE_PATH to an installed Chrome/Chromium.
 *
 * HOW IT WORKS
 *   1. `npm run build` + `vite preview` serve the production bundle.
 *   2. Puppeteer opens a 1920×1080 page, clicks PLAY, and screen-records the
 *      stage in realtime while the audio clock drives every animation.
 *   3. ffmpeg muxes the raw capture with public/assets/audio/voiceover.mp3
 *      and writes final.mp4 (H.264, AAC) + a 10 s preview.gif teaser.
 *
 * RUN:  node scripts/render-video.js
 */
const { exec } = require('child_process');
const { promisify } = require('util');
const path = require('path');
const fs = require('fs');

const execPromise = promisify(exec);
const ROOT = path.resolve(__dirname, '..');
const PREVIEW_URL = process.env.PREVIEW_URL || 'http://localhost:4173';
const START_ON_PAGE = true; // clicks the PLAY overlay automatically

async function renderVideo() {
  console.log('🎬 Building production bundle…');
  await execPromise('npm run build', { cwd: ROOT });

  console.log('🚀 Starting vite preview…');
  const preview = execPromise('npx vite preview --port 4173 --strictPort', { cwd: ROOT });
  await new Promise((r) => setTimeout(r, 3000));

  const browser = await require('puppeteer').launch({
    headless: 'new',
    args: [
      '--no-sandbox',
      '--disable-setuid-sandbox',
      '--autoplay-policy=no-user-gesture-required',
      '--use-gl=angle',
      '--enable-gpu-rasterization',
    ],
  });
  const page = await browser.newPage();
  await page.setViewport({ width: 1920, height: 1080, deviceScaleFactor: 1 });
  await page.goto(PREVIEW_URL, { waitUntil: 'networkidle0', timeout: 90000 });

  if (START_ON_PAGE) {
    await page.evaluate(() => {
      sfxReady();
      function sfxReady() { /* app unlocks audio on its own play() call */ }
      document.querySelector('.start-overlay')?.click();
    });
  }

  const durationSec = 633; // 10:32 voiceover + tail
  console.log(`🎥 Recording ${durationSec}s at 30fps…`);
  const recorder = new (require('puppeteer-screen-recorder').PuppeteerScreenRecorder)(page, {
    fps: 30,
    videoBitrate: 8000,
    videoCodec: 'libx264',
    aspectRatio: '16:9',
  });
  await recorder.start(path.join(ROOT, 'output-video-raw.mp4'));
  await new Promise((r) => setTimeout(r, durationSec * 1000));
  await recorder.stop();
  await browser.close();

  console.log('🔊 Muxing voiceover…');
  await execPromise(
    `ffmpeg -y -i output-video-raw.mp4 -i public/assets/audio/voiceover.mp3 ` +
      `-c:v libx264 -crf 18 -preset medium -pix_fmt yuv420p -c:a aac -b:a 192k ` +
      `-map 0:v:0 -map 1:a:0 -shortest final.mp4`,
    { cwd: ROOT }
  );

  console.log('🎞 Creating preview.gif (first 10 s)…');
  await execPromise(
    `ffmpeg -y -i final.mp4 -t 10 -vf "fps=15,scale=800:-1:flags=lanczos,split[s0][s1];[s0]palettegen[p];[s1][p]paletteuse" preview.gif`,
    { cwd: ROOT }
  );

  fs.rmSync(path.join(ROOT, 'output-video-raw.mp4'), { force: true });
  preview.child?.kill?.();
  console.log('✅ final.mp4 + preview.gif created.');
}

renderVideo().catch((e) => {
  console.error(e);
  process.exit(1);
});
