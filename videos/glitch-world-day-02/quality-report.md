# Quality Report — Day 02: "HE KNOWS MY NAME"

All numbers below were measured from the actual rendered/encoded files, not estimated.
Rendering, mixing, and QC use only the local virtualenv (Pillow/NumPy/ffmpeg); no paid
APIs or external rendering services were used.

## 1. Final deliverable verification (`day-02-he-knows-my-name.mp4`)

| Property | Requirement | Measured result | Pass |
|---|---|---|---|
| Resolution | 1080 × 1920 (9:16) | 1080 × 1920 | ✅ |
| Frame rate | constant 30 fps | 30 fps, 30 tbr; 3902 frames over 130.07 s (CFR) | ✅ |
| Frame count | exact 30 fps timeline | 3902 frames | ✅ |
| Video codec | H.264 MP4 | H.264 High, yuv420p, progressive, ~4.3 Mbps, faststart | ✅ |
| Audio codec | AAC | AAC-LC, 48000 Hz, stereo, 192 kbps | ✅ |
| Container duration | matches narration | 2:10.07 (narration source 130.037 s) | ✅ |
| Integrated loudness | −14 to −16 LUFS | **−14.7 LUFS** (measured on the muxed AAC) | ✅ |
| True peak | ≤ −1 dBTP | **−1.2 dBFS** (measured on the muxed AAC) | ✅ |
| Loudness range | controlled | 4.3 LU | ✅ |
| Burned-in subtitles | yes | present; in-world text cues (9/12/36/37) suppressed to avoid double text | ✅ |
| Separate SRT | yes | `day-02-he-knows-my-name.srt`, 39 cues, full transcript | ✅ |
| Watermarks | none | none | ✅ |
| Black frames | none | `blackdetect` 0 events; per-frame scan near-black count = **0** | ✅ |
| Frozen frames | none | `freezedetect` 0 events (per-frame grain guarantees unique frames; long low-motion holds are intentional, not stuck) | ✅ |
| Ending | no black/freeze | last 6 frames stable at mean brightness ≈13.9, choice cards fully visible | ✅ |

Per-frame brightness scan (all 3902 frames decoded and streamed one at a time):
min 6.8 / mean 13.4 / max 19.2 (0–255 scale) — no outliers beyond the intentional
night palette, and no near-black frames anywhere including the tail.

## 2. Defects found in QC and how each was resolved

The whole video was reviewed scene by scene (8 contact sheets plus targeted full-resolution
frames), every issue was collected first, then fixed together.

1. **Magenta chromatic tear bars on scene transitions** — `slice_tear` was dropping colored
   tints; set `tint=None` so tears are neutral displacement only.
2. **Alley "bright dome" washout / unreadable carved text (root cause)** — transparent radial
   glows carried full RGB at alpha 0; dropping alpha (`convert("RGB")`, raw rgb24 pipe) baked
   RGB ghosts. `radial()` now zeroes RGB below an alpha threshold of 8, and the renderer
   flattens every frame onto an opaque `(5,7,16)` base via masked paste instead of converting.
   A dark blurred plate behind the text and brighter carved grooves finish the fix. Verified:
   no dome, "STOP LOOKING FOR ME" and "LOOK UP" are legible.
3. **Oversized key prop** — `key_prop` rewritten small and self-centering.
4. **Choice-card collision** — cards restacked into non-overlapping bands with A/B badges and
   safe margins.
5. **Floating figure / building with no roofline** — building widened, roof slab added, mystery
   figure placed correctly proportioned on the roof (no giant).
6. **Rooftop framing / wrist timer** — two-shot reframed; hero timer stays 98D, his wrist
   reads 00:00:00 clearly.
7. **Staircase rotation readability** — rebuilt as a 4-step perspective climb with two
   mechanical direction shifts and a snap-back stumble.
8. **Montage lamp/arm/label glitches** — citizen-cup rig corrected; on-screen labels removed.
9. **City head-turn too small to read** — the synchronized turn now holds a wide row of five
   citizens whose heads rotate together and flare cyan, with two brief close-ups inside the beat.
10. **OPEN-sign overlap** — sign repositioned high and clear of the sidewalk.
11. **Vanish effect full-frame bands / crossing streak** — `_segment_vanish` rebuilt as six
    strips strictly inside the figure bounding box (x ±200, y −330..+90), shift ≤26 px, alpha
    fade; the cyan center line that crossed both characters was deleted.
12. **Sky fracture read as a giant humanoid/exploding figure (root cause)** — the old branching
    generator happened to form a body-shaped silhouette. Redesigned as near-vertical zigzag
    cracks with short branches and displaced rectangular sky fragments, clipped to the sky
    region so nothing touches the characters or reads as a figure.
13. **Ending faded to black (3 near-black tail frames)** — removed the end fade; the final
    glitch now settles onto a stable, fully visible frame holding both choice cards. Re-scan
    confirms zero near-black frames.

## 3. Canon compliance (locked story elements)

- Hero countdown always **98D 11:42:06** (verified on street and choice frames).
- Mystery stickman wrist reads **00:00:00** — his timer only; the hero's never changes.
- Wall messages carved in stone: "STOP LOOKING FOR ME" then "LOOK UP".
- Impossible building materializes; figure stands correctly sized on the roof.
- Staircase changes direction; he nearly falls.
- Rooftop: "I'm the reason you're still alive"; sky fractures; "the world doesn't restart. YOU do."
- Every citizen turns their head in exact synchronization (wide row + cyan head flares).
- Key transfer; "Find the room with no door"; don't-trust-tomorrow warning; segment disappearance.
- Ending choice A (cyan, door glyph) "SEARCH FOR THE ROOM WITH NO DOOR";
  choice B (magenta, eye glyph) "FIND OUT WHY EVERYONE IS WATCHING ME" — exact wording.

## 4. Voiceover integrity

- Source: the Adam narration MP3 from connected Google Drive (130.037 s), preserved untouched
  in `assets/audio/source/`. No TTS replacement, no re-voicing, no pitch or tempo alteration.
- The full 130.04 s timeline and all 39 cues are driven from `voiceover-timing.json`.
- Narration is only level-normalized at the mastering stage; the waveform is never edited.
- No mismatch was found between the delivered MP3 and the reference script; the 39 measured
  sentence cues match the expected narration beat-for-beat.

## 5. Reproducibility / provenance

- Picture: `project/pipeline/render.py` (deterministic seeded RNG; libx264 CRF 19).
- Sound: `sound_engine.py` (seeded procedural synthesis) → `mix.py` (sidechain ducking, limiter)
  → ffmpeg `loudnorm I=-15 TP=-1.5` to keep the encoded AAC true peak ≤ −1 dBTP.
- Regenerable large intermediates (stems, pre/final WAV, picture-only MP4) are git-ignored;
  the mastered MP4, source audio, code, timing JSON, SRT, docs, and contact sheets are retained.

## 6. Known limitations / honest notes

- Procedural stick figures and abstract backgrounds are intentionally stylized, not hand-drawn art.
- The standalone `.srt` is the complete transcript (including the in-world messages and A/B lines)
  for accessibility; on the burned-in picture those four cues are intentionally omitted because
  the identical words already appear as in-world typography.
- Audio true peak is specified against the final AAC encode; the PCM master is rendered with a
  −1.5 dBTP ceiling to leave headroom for the AAC codec.
