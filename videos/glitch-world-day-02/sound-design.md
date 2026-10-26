# Sound Design — Day 02: "HE KNOWS MY NAME"

## Creative direction
Minimal-music, atmosphere-first production. There is **no music track and no licensed library content**; the entire soundtrack is synthesized from filtered noise and simple oscillators so the narration stays dominant and the "glitched world" reads through sound rather than melody. Tension is carried by a barely-audible low drone and by negative space, never by a score.

The delivered narration (`assets/audio/source/day-02-voiceover-source.mp3`, Adam, 130.037 s) is the authoritative timing source and is **never pitch-shifted, time-stretched, or edited**. It is only level-normalized at the mastering stage.

## Signal chain
1. `project/pipeline/sound_engine.py` synthesizes every layer at **48 kHz** with a fixed RNG seed (11), writing separate stems to `assets/audio/stems/` (NumPy):
   `bed_street`, `bed_room`, `bed_wind`, `fx`, `drone`, and the summed `effects_mix`.
2. `project/pipeline/mix.py` loads the 48 kHz narration, applies **sidechain ducking** to the effects bed (50 ms RMS voice detection, 45% maximum dip, smoothed attack/release), sums the beds + narration, and runs a soft safety limiter → `assets/audio/day-02-mix-pre.wav`.
3. ffmpeg **EBU R128 loudnorm** (I = −15 LUFS, LRA = 11, PCM TP ceiling = −1.5) masters
   `assets/audio/day-02-final-mix.wav`. The ceiling is set to −1.5 rather than −1.0 because the
   later AAC encode adds ~0.2–0.3 dB of true-peak overshoot; leaving headroom keeps the final
   deliverable at or below −1 dBTP. Both stages are verified independently with `ebur128`.

### Measured master results
| Metric | Target | PCM master | Final AAC in MP4 |
|---|---|---|---|
| Integrated loudness | −14 to −16 LUFS | −14.6 LUFS | **−14.7 LUFS** |
| Loudness range | ≤ 11 LU | 4.2 LU | 4.3 LU |
| True peak | ≤ −1 dBTP | −1.5 dBFS | **−1.2 dBFS** |
| Sample rate | 48 kHz | 48 kHz | 48 kHz |
| Channels | stereo | stereo | stereo |

## Layer inventory
- **City bed (`bed_street`)** — 60/90 Hz electrical hum + low-passed air, only under street/city-turn segments (0–50.79 s and 94.76–99.11 s).
- **Room tone (`bed_room`)** — narrow-band low-passed noise for the door corridor (28.95–34.01 s) and stairwell (57.43–63.50 s).
- **Wind bed (`bed_wind`)** — 120–900 Hz band-passed noise with a slow LFO swell, introduced at the building reveal and continuous across the rooftop act (50.79–57.43 s, 63.50–130.04 s).
- **Tension drone (`drone`)** — 48/72 Hz sine stack at a very low level (~0.06 gain), swelling gradually through the rooftop confrontation; LFO keeps it alive without becoming musical.

## Foley & one-shots (all procedural)
| Cue / time | Event | Sound |
|---|---|---|
| 13.0–15.9, 16.8–26.4, 34.4–36.4 | walking | band-passed noise step + 95→60 Hz thump, randomized cadence/pan |
| 57.7–59.4 | stair run | faster, louder footstep cadence |
| sparse, see `sound_engine` event list | anomalies | short 0.9–6.5 kHz band-passed chirp + FM tone ("glitch") |
| 16.36 / 50.79 / 57.43 / 63.50 / 109.80 | scene tears | 0.3–9 kHz noise tear + 220→1400 Hz sweep |
| cue 9 & 12 | wall carvings | long 1.2–5.2 kHz gritty scrape, confirmation thud after "STOP LOOKING FOR ME" |
| 51.0 s | building materialization | 120 Hz rumble swell + bright settle glitch |
| 59.13 / 60.93 s | staircase shifts | sub rumble + tear; metal railing rattle (clink) |
| cue 20–24 | wrist zero reveal | 420 Hz activation pulse, two 880 Hz readout pulses, settle distortion |
| cues 25–26 | sky breaking | 4.5 s low rumble + four alternating-pan 2.6 kHz cracks |
| end of cue 28 ("YOU do") | restrained impact | 46 Hz three-oscillator drone hit, ~1.8 s decay |
| cue 29 +0.55 s | synchronized head turn | single 130 Hz mechanical pulse + centered filtered sweep; cyan head flares are visual only |
| cues 30–31 | key transfer | 1.8/2.65 kHz metallic clink + 660→520 Hz resonant tone |
| cue 32 | don't-trust-tomorrow | off-center phase-shift glitch |
| cue 33 | disappearance | interference chirp + digital tear + 38 Hz drop |
| cues 36/37 | choice cards | 520 Hz (A, cyan) and 392 Hz (B, magenta) UI pulses |
| end −0.4 s | final glitch | short tear into the clean end frame |

## Mixing notes
- Sidechain ducking only ever lowers the **effects** bed; the narration waveform is untouched.
- One-shots are sparse and low-level (most 0.3–0.6 gain) so they register as diegetic texture, not sound effects spectacle.
- No element is allowed to exceed the −1 dBTP ceiling; loudnorm's true-peak limiter is the final guard.
- Reproduction: `python sound_engine.py && python mix.py`, then the ffmpeg loudnorm command documented in `README.md`.
