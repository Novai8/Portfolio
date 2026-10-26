# Day 02 — "HE KNOWS MY NAME"

Episode 2 of *100 Days Trapped in a Glitched World* — a fully procedural, vertical (1080×1920, 30 fps) animated short built in Python (Pillow + NumPy), with a synthesized sound design bed mixed under the original recorded narration.

## Deliverables

```
videos/glitch-world-day-02/
├── day-02-he-knows-my-name.mp4          # final H.264 + AAC master (burned-in subtitles)
├── day-02-he-knows-my-name.srt          # standalone subtitle track (39 cues)
├── voiceover-timing.json                # measured per-sentence timing (timeline source of truth)
├── storyboard.md                        # scene-by-scene visual storyboard and canon locks
├── sound-design.md                      # synthesized audio layers, events, and loudness results
├── quality-report.md                    # QC findings, fixes, and final technical verification
├── README.md
├── assets/
│   ├── audio/
│   │   ├── source/                      # pristine Drive narration (mp3) + 48 kHz wav
│   │   ├── stems/                       # procedural sound stems (.npy)
│   │   ├── day-02-mix-pre.wav           # pre-master (ducked, limited)
│   │   └── day-02-final-mix.wav         # R128 master (−14.6 LUFS / −1.0 dBTP)
│   ├── fonts/                           # bundled OFL fonts
│   ├── rigs/ backgrounds/ props/        # reusable visual asset definitions
├── project/pipeline/
│   ├── engine/                          # config, easing, draw helpers, rig, effects, world, subtitles
│   ├── shots/                           # 8 scene modules (street … choices)
│   ├── render.py                        # frame renderer + H.264 ffmpeg pipe / contact sheets
│   ├── sound_engine.py                  # procedural audio synthesis
│   └── mix.py                           # narration + effects mixing and ducking
├── renders/
│   └── video-only.mp4                   # rendered picture (no audio) before mux
└── preview/
    ├── contact-01..08_*.png             # per-scene QC contact sheets
    └── storyboard-contact-sheet.png     # canonical one-page storyboard sheet
```

## The golden rule: narration defines the timeline
The authoritative asset is the Adam narration MP3 retrieved from connected Google Drive
(`assets/audio/source/day-02-voiceover-source.mp3`, measured **130.037 s**). Every scene,
effect, and sound event is scheduled from `voiceover-timing.json` (39 sentence cues derived
from that file). The voice is never replaced by TTS, never re-voiced, and never pitch-shifted
or time-stretched; mastering changes loudness only.

## Reproduction (all offline, no paid services)
Uses the project virtualenv (`numpy`, `pillow`, `mutagen`, `imageio-ffmpeg`); ffmpeg is invoked
from the same environment.

```bash
cd project/pipeline

# 0. Regenerate the 48 kHz working WAV from the authoritative source MP3 (git-ignored)
ffmpeg -y -i ../../assets/audio/source/day-02-voiceover-source.mp3 \
  -ar 48000 -ac 2 -c:a pcm_s24le ../../assets/audio/source/day-02-voiceover-48k.wav

# 1. Picture: renders every frame and pipes raw rgb24 into libx264
python render.py --out ../../renders/video-only.mp4

# 2. Contact sheets instead of a full render (QC)
python render.py --preview --every 1.5 --scene rooftop

# 3. Procedural sound stems and the ducked pre-master
python sound_engine.py
python mix.py

# 4. R128 master (48 kHz, −15 LUFS target; −1.5 dBTP ceiling leaves headroom
#    so the later AAC encode still measures ≤ −1 dBTP)
ffmpeg -y -i ../../assets/audio/day-02-mix-pre.wav \
  -af loudnorm=I=-15:TP=-1.5:LRA=11 -ar 48000 -c:a pcm_s24le \
  ../../assets/audio/day-02-final-mix.wav

# 5. Mux picture + audio + burned subtitles are already in picture; attach SRT metadata
ffmpeg -y -i ../../renders/video-only.mp4 -i ../../assets/audio/day-02-final-mix.wav \
  -map 0:v:0 -map 1:a:0 -c:v copy -c:a aac -b:a 192k -ar 48000 \
  -movflags +faststart ../../day-02-he-knows-my-name.mp4
```

## Technical spec
- Picture: 1080×1920, **constant 30 fps**, H.264 (libx264, CRF 19, yuv420p, faststart)
- Audio: AAC, **48 kHz stereo**, 192 kbps; final AAC measured −14.7 LUFS integrated, −1.2 dBTP
- Subtitles: burned into the picture **and** shipped as a separate `.srt`
- No watermarks, no black frames, no frozen frames; hard scene transitions use digital tears

## Story canon (locked)
Hero timer always **98D 11:42:06**; the mystery stickman's wrist reads **00:00:00** (his timer
only). Key lines, the synchronized city head-turn, the key transfer, the "room with no door"
instruction, the don't-trust-tomorrow warning, his segment disappearance, and the exact
cyan/magenta ending choices are documented in `storyboard.md` and enforced by the scene code.
