# Executive Search Inbox Assistant — Demo Video

Fully procedural 2:43 UI demo video, frame-synced to a voiceover.
Thread summary → next actions → draft reply (human-approved) → audit log.

## Deliverables (`deliverables/`)
- `Inbox_Assistant_Demo_FINAL.mp4` — 1920×1080, 30 fps, main mix
- `Inbox_Assistant_Demo_lighter_SFX.mp4` / `Inbox_Assistant_Demo_stronger_SFX.mp4` — SFX −5 dB / +4 dB
- `Inbox_Assistant_Demo.srt` — subtitles (sentence case, max 2 lines)

## How it's built
- `src/beats.py` — master beat sheet: scene ranges, word-timed cues, SFX event list, locked fictional data
- `src/scenes.py` — 18 scenes drawn with Pillow (cards, chips, cursor, checkmarks, counters)
- `src/render.py` — compositor: transitions (zoom-blur, parallax slide, title card), camera push-ins, subtitles
- `src/ui.py` / `src/style.py` — design system, easing, overflow guard, on-screen string collection for spellcheck
- `src/audio.py` — procedural music bed + UI SFX palette (numpy/scipy)
- `mix.sh` — ffmpeg encode: VO-first mix (music −20 dB, SFX −15 dB)
- `transcript.json` — word-level VO timestamps used for sync

## Reproduce
```bash
pip install pillow numpy scipy imageio-ffmpeg faster-whisper pyspellchecker
ffmpeg -i audio_stems/vo.mp3 -ar 48000 -ac 1 vo.wav
python3 src/audio.py .                    # sfx.wav, music.wav
python3 src/render.py 0 4920 frames       # frames
./mix.sh 0 final.mp4 frames
```

All data is fictional. Independent portfolio prototype; results vary.
