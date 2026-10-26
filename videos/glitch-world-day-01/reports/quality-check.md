# Quality check — Glitch World, Day 1

Rendered file: `final/glitch-world-day-01.mp4`  
Duration: **113.790s** · 1080x1920 · 30 fps · H.264 + AAC 48 kHz · 29.7 MB  
Source voiceover: `audio/original-voiceover.mp3` (113.789s measured)

**27/27 automated checks passed.**

| check | result | detail |
|---|---|---|
| final MP4 exists | ✅ pass | /home/user/Portfolio/videos/glitch-world-day-01/final/glitch-world-day-01.mp4 |
| video stream is H.264 | ✅ pass | Stream #0:0[0x1] |
| resolution 1080x1920 | ✅ pass | 1080x1920 |
| pixel format yuv420p | ✅ pass | yuv420p |
| frame rate 30 fps | ✅ pass | 30 fps |
| audio stream is AAC | ✅ pass | Stream #0:1[0x2](und): Audio: aac (LC) (mp4a / 0x6134706D) |
| audio 48 kHz | ✅ pass | 48000 Hz |
| duration matches the voiceover (+/- 100 ms) | ✅ pass | 113.790s vs VO 113.789s |
| deliverable is under GitHub's 100 MB file limit | ✅ pass | 29.7 MB |
| frame count matches 30 fps cadence | ✅ pass | 3413 frames (expected ~3414) |
| no black frames | ✅ pass | 0 frames under 6/255 luma |
| no accidental frozen stretches | ✅ pass | longest identical run 0 frames |
| motion present throughout | ✅ pass | mean frame delta 1.15 |
| audio length matches the video | ✅ pass | 113.792s vs 113.790s |
| narration is present across the whole recording | ✅ pass | 42/42 speech segments audible, min RMS 0.045 |
| no unintended silent gaps | ✅ pass | 0 silent 250 ms windows |
| true peak below -1.0 dBFS | ✅ pass | -1.10 dBFS |
| no abrupt audio cutoff at the end | ✅ pass | last 50 ms peak 0.002 |
| SRT file present and parses | ✅ pass | 50 cues |
| SRT ends at the end of the film | ✅ pass | last cue ends 113.64s |
| SRT cues never overlap | ✅ pass | min gap 0.000s |
| SRT cues are caption-sized | ✅ pass | 0 overlong cues |
| subtitle text covers the spoken script | ✅ pass | missing tokens: [] |
| timeline covers the whole recording | ✅ pass | 113.79s of 113.79s |
| no gaps between shots | ✅ pass | [] |
| captions sit above platform UI safe area | ✅ pass | caption band centre y=1372px, limit 1574px |
| captions keep clear of the right-edge action rail | ✅ pass | right margin 132px |

## Visual review

- Storyboard and contact sheet regenerated from the exported MP4: `previews/storyboard.jpg`, `previews/contact-sheet.jpg`.
- Every shot was reviewed as a still; the protagonist rig, line weight and palette were held constant across all 11 shots.
- Captions use Inter ExtraBold, white with a dark outline, inside a plate, clear of the bottom UI band and the right-hand action rail.
- In-world type (REALITY UPDATE FAILED / RESTARTING IN 100 DAYS / YOU'RE NOT REAL / the countdown / the A-B choice) is drawn with a separate display + mono typography so it is never confused with dialogue captions.
