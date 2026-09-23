# 🎬 The 2:07 A.M. Order — Interactive Motion Video

An ultra-dynamic, word-synced motion-graphics experience telling the true-ish
story of a midnight e-commerce scam attempt: 500 planners, $12,480, an
abandoned warehouse — and why getting (almost) scammed upgraded the business.

**▶ Live preview:** run `npm run dev` in this folder and open the printed URL.

- ✨ **18 uniquely styled scenes** — paper cutout → neon dashboard → comic-book
  reveal → EKG parkour → map noir → conspiracy corkboard → ransom note → tech
  lockdown → sunrise ending. Zero static frames: every scene has continuous
  background motion, looping layer animation and beat-gated reveals.
- 🎤 **Word-by-word audio sync with zero drift** — all 1,291 words are aligned
  to the 10:32 voiceover; captions, kinetic type, scene cuts and SFX all read
  from one master clock (the `<audio>` element polled by rAF — no wall-clock
  timers, so pause/seek/tab-throttle can never desync it).
- 🔊 **123 scheduled sound events across 97 procedural recipes** — synthesized
  live with the Web Audio API (Howler manages context unlock), so nothing
  ever stalls on a network request.
- 🎮 **Interactive UI** — play/pause, ±10 s, chapter-segmented scrub bar with
  hover tooltips, 18-chapter menu, caption toggle (C), SFX toggle (M),
  fullscreen, debug overlay (D: clock, word index, scene, FPS; P: audition
  every SFX recipe).

## 🚀 Quick start

```bash
npm install
npm run dev        # interactive experience (dev)
npm run build      # production bundle → dist/
npm run preview    # serve the production build

npm run render:video   # final.mp4 + preview.gif (needs ffmpeg + Chromium, see below)
```

## 🎨 Tech stack

| Layer | Choice |
|---|---|
| Framework | React 18 + TypeScript + Vite 5 |
| Animation | GSAP 3 (timelines, transitions, caption pops) + CSS keyframes (60 fps compositor loops) + Framer Motion (UI micro-interactions) |
| Audio | HTMLAudio master clock · WebAudio synth engine · Howler (context lifecycle) |
| Alignment | pocketsphinx forced alignment + DP (see `scripts/transcribe.py`) |
| Video export | Puppeteer screen recording + ffmpeg mux (`scripts/render-video.js`) |

## 🕐 The timing data (why sync can't drift)

`src/data/` holds the generated ground truth:

- `word_timestamps.json` — 1,291 words with `{word, start, end, conf}`,
  force-aligned against the **actual audio** (both takes, part 2 offset by
  part 1 + a 0.35 s seam). Verified: fully monotonic, spot-checked at 10+
  points (`$12,480.` lands at 47.85 s, `"Five…` at 58.22 s, `spine` at
  631.15 s).
- `chunks.json` — 214 caption lines (sentence-grouped) covering every word.
- `scenes.json` — **real** 18-scene boundaries measured from anchor phrases
  (the storyboard's estimated 10:26 timeline shifted slightly once measured
  against the real 10:32 audio — the data wins over the estimate).
- `anchors.json` — 157 phrase→timestamp anchors used by scenes for beat-gated
  reveals (`anchorLocal(sceneId, key)`).
- `sfx_timeline.json` — 123 SFX events, each resolved to an anchor phrase,
  fired when the audio clock crosses their timestamp (seeks re-arm safely).

`public/captions/captions.vtt` + `.srt` carry the same timings for players.

## 📂 Structure

```
planner-scam-interactive/
├── index.html
├── public/
│   ├── assets/audio/voiceover.mp3     # combined master (both takes, 10:32)
│   └── captions/captions.vtt|.srt
├── src/
│   ├── App.tsx                        # orchestrator: clock, scenes, UI
│   ├── components/                    # MotionBackground, WordHighlight,
│   │                                  # SceneTransition, InteractiveUI, DebugOverlay
│   ├── scenes/                        # Scene01…Scene18 + kit.tsx (shared kit)
│   ├── lib/                           # audioSync, sfxManager, sfxTimeline, animationHelpers
│   ├── data/                          # generated timing JSONs
│   └── styles/                        # global.css, animations.css
├── scripts/                           # transcribe.py, render-video.js
└── captions/                          # caption artifacts
```

## 🎯 Scene breakdown (measured start times)

| # | Scene | Start | Template |
|---|---|---|---|
| 01 | Late Night Launch | 0:00 | paper-cutout collage, 2:07 clock, cereal-pour particles |
| 02 | The Planner Business | 0:12 | peach/mint product UI, 3D planner carousel, sticker |
| 03 | Dashboard Refresh | 0:30 | neon holographic dashboard, cursor mashing refresh |
| 04 | THE BIG REVEAL | 0:39 | comic explosion, 500 spin-up, $12,480 dollar rain |
| 05 | Heart Parkour | 1:02 | EKG monitor, parkour heart, lumbar-support dream |
| 06 | Warehouse Discovery | 1:25 | map noir, pin drop, spotlight warehouse, 🦝 |
| 07 | Three Possibilities | 1:55 | minimalist infographic, Venn glow, paw prints |
| 08 | Email Exchange | 2:15 | dark inbox, typing dots, urgent badges |
| 09 | Brain Spiral | 2:41 | conspiracy corkboard, red string, stress meter |
| 10 | Living Room Office | 2:54 | isometric blueprint room, morphing furniture |
| 11 | Maya's Wisdom | 3:08 | split-screen call, bubbles, DO NOT SHIP stamp |
| 12 | Investigation | 3:45 | browser noir, auto-typing searches, NOTHING stamps |
| 13 | Escalation Emails | 4:14 | red alert, 14:00 countdown, icy edges, glass crack |
| 14 | Payment Call | 4:48 | support UI, sad hold-music bars, HIGH RISK badge |
| 15 | Threat Email | 5:42 | ransom-note letters, puzzle click, scheme flowchart |
| 16 | Security Lockdown | 6:59 | tech grid, six toggles, traffic graph red→green |
| 17 | Laughter & Realization | 8:17 | confetti, HA-HA bounce, expectation vs reality |
| 18 | Happy Ending | 9:07 | sunrise, verified card, growth chart, “ship your spine first” |

## 📹 Video export

**`final.mp4` (1080p, 10:32) and `preview.gif` (10 s teaser) are committed** —
rendered with the offline canvas pipeline:

```bash
npm run render:offline    # canvas-render every frame → final.mp4 + preview.gif
```

`scripts/offline/render.mjs` draws all 18 scenes on `@napi-rs/canvas`
(same 1600×900 design space, scaled to 1920×1080, real Google fonts) and
streams frames into the `@ffmpeg-installer` ffmpeg muxed with the voiceover —
no browser required, ~1 minute of wall time. Flags: `--qa` (stills), `--bench`
(speed estimate), `FPS=` env override.

`npm run render:video` remains as an alternative that screen-records the live
React app via Puppeteer (needs ffmpeg + a Chromium binary on the machine).

## 🔊 Sound design

- VO at full level through `<audio>`; SFX synthesized on a compressed bus
  (default 50%, toggled with M) — never overpowering the narration.
- 97 recipes across UI / motion / emotional / alert / success / phone /
  ambient categories; audition them all with the `P` key in the debug overlay.

## 📝 License

Code: MIT. Voiceover audio: licensed ElevenLabs generation (in-repo takes).
