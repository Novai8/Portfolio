#!/usr/bin/env python3
"""
Procedural sound design for Glitch World Day 02 (no external SFX libraries).

All layers are synthesized at 48 kHz from noise + oscillators, arranged against
the measured voiceover timing map, then mixed with the untouched narration.
Outputs separate stems plus the final stereo mix.
"""
import json, math, os, sys
import numpy as np

SR = 48000
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
TIMING = os.path.join(ROOT, "voiceover-timing.json")
OUT = os.path.join(ROOT, "assets", "audio", "stems")
os.makedirs(OUT, exist_ok=True)

rng = np.random.default_rng(11)

# ----------------------------------------------------------------- primitives
def nframes(sec): return int(sec * SR)

def white(sec):
    return rng.normal(0, 1, nframes(sec)).astype(np.float32)

def _lp_fast(x, a):
    """First-order low-pass y[n]=a*y[n-1]+(1-a)*x[n], stable vectorized EMA."""
    x = x.astype(np.float64)
    b = 1 - a
    y = np.empty(len(x), np.float64)
    init = 0.0
    CH = 256  # small enough that a**n never underflows in float64
    for i in range(0, len(x), CH):
        chunk = x[i:i + CH]
        n = np.arange(1, len(chunk) + 1)
        decay = a ** n
        ema = b * decay * np.cumsum(chunk / decay)
        y[i:i + len(chunk)] = ema + init * decay
        init = y[i + len(chunk) - 1]
    return y.astype(np.float32)

def hp(x, cutoff):
    return x - _lp_fast(x, math.exp(-2 * math.pi * cutoff / SR))

def bp(x, lo, hi):
    return _lp_fast(hp(x, lo), math.exp(-2 * math.pi * hi / SR))

def env(n, attack=0.01, release=0.1, sustain=1.0):
    a = nframes(attack); r = nframes(release)
    e = np.ones(n, np.float32) * sustain
    if a > 0: e[:a] = np.linspace(0, sustain, a)
    if r > 0 and r < n: e[-r:] = np.linspace(sustain, 0, r)
    return e

def sine(sec, f, f2=None):
    t = np.arange(nframes(sec)) / SR
    if f2:
        f = np.linspace(f, f2, nframes(sec))
        phase = 2 * np.pi * np.cumsum(f) / SR
    else:
        phase = 2 * np.pi * f * t
    return np.sin(phase).astype(np.float32)

def place(track, sig, at, gain=1.0, pan=0.0):
    i = nframes(at)
    if i >= len(track): return
    end = min(len(track), i + len(sig))
    seg = sig[:end - i] * gain
    if track.ndim == 2:
        l = math.cos((pan + 1) * math.pi / 4); r = math.sin((pan + 1) * math.pi / 4)
        track[i:end, 0] += seg * l
        track[i:end, 1] += seg * r
    else:
        track[i:end] += seg

def stereo():
    return np.zeros((nframes(DUR), 2), np.float32)

# ----------------------------------------------------------------- one-shots
def sfx_footstep(sec=0.12):
    x = white(sec)
    x = bp(x, 180, 2400) * env(len(x), 0.002, 0.09)
    thump = sine(sec * 0.5, 95, 60) * env(nframes(sec * 0.5), 0.002, 0.08)
    out = np.zeros(nframes(sec), np.float32)
    out[:len(thump)] += thump * 0.6
    out[:len(x)] += x
    return out * 0.5

def sfx_glitch(sec=0.18, bright=1.0):
    x = white(sec)
    x = bp(x, 900, 6500) * env(len(x), 0.002, sec * 0.7)
    tone = sine(sec, 1400 * bright, 700 * bright) * env(len(x), 0.002, sec * 0.6) * 0.25
    return (x * 0.5 + tone).astype(np.float32)

def sfx_tear(sec=0.22):
    x = white(sec)
    x = bp(x, 300, 9000)
    sweep = sine(sec, 220, 1400) * 0.3
    e = env(len(x), 0.004, sec * 0.8)
    return (x * e * 0.5 + sweep * e).astype(np.float32)

def sfx_drone_hit(sec=1.6, f=52):
    t = np.arange(nframes(sec)) / SR
    sig = (np.sin(2 * math.pi * f * t) + 0.5 * np.sin(2 * math.pi * f * 1.5 * t)
           + 0.25 * np.sin(2 * math.pi * f * 2.01 * t))
    e = np.exp(-t * 2.2)
    return (sig * e).astype(np.float32)

def sfx_pulse(sec=0.3, f=110):
    t = np.arange(nframes(sec)) / SR
    return (np.sin(2 * math.pi * f * t) * np.exp(-t * 9)).astype(np.float32)

def sfx_scrape(sec=1.4):
    x = white(sec)
    x = bp(x, 1200, 5200)
    # irregular gritty amplitude
    t = np.arange(len(x)) / SR
    grit = 0.5 + 0.5 * np.sin(2 * math.pi * 9 * t) * rng.uniform(0.3, 1, len(x))
    return (x * grit * env(len(x), 0.05, sec * 0.6) * 0.4).astype(np.float32)

def sfx_clink(sec=0.4):
    t = np.arange(nframes(sec)) / SR
    sig = (np.sin(2 * math.pi * 1800 * t) + 0.6 * np.sin(2 * math.pi * 2650 * t))
    return (sig * np.exp(-t * 12) * 0.35).astype(np.float32)

def sfx_rumble(sec=3.0):
    x = _lp_fast(white(sec), math.exp(-2 * math.pi * 120 / SR))
    t = np.arange(len(x)) / SR
    swell = np.clip(np.sin(math.pi * t / sec), 0, 1)
    return (x * swell * 0.7).astype(np.float32)

def sfx_crack(sec=0.5):
    x = white(sec)
    hi = hp(x, 2600) * env(len(x), 0.001, 0.4) * 0.4
    lo = _lp_fast(white(sec), math.exp(-2 * math.pi * 220 / SR)) * env(len(x), 0.002, 0.45)
    return (hi + lo * 0.8).astype(np.float32)

# ----------------------------------------------------------------- beds
def gen_wind(sec, level=0.5, lfo=0.13):
    x = bp(white(sec), 120, 900)
    t = np.arange(len(x)) / SR
    amp = level * (0.7 + 0.3 * np.sin(2 * math.pi * lfo * t))
    return (x * amp).astype(np.float32)

def gen_city(sec, level=0.16):
    hum = sine(sec, 60) * 0.4 + sine(sec, 90) * 0.2
    air = _lp_fast(white(sec), math.exp(-2 * math.pi * 500 / SR)) * 0.5
    return ((hum + air) * level).astype(np.float32)

def gen_room(sec, level=0.12):
    return (_lp_fast(white(sec), math.exp(-2 * math.pi * 300 / SR)) * level).astype(np.float32)

# ----------------------------------------------------------------- arrange
def main():
    global DUR
    timing = json.load(open(TIMING))
    DUR = timing["measured_duration_s"]
    cues = timing["sentences"]
    def c(i): return cues[i]

    bed_street, bed_room, bed_wind, fx, drone = (stereo() for _ in range(5))

    def mono_to(track, sig, at, gain=1.0, pan=0.0):
        place(track, sig, at, gain, pan)

    # --- ambient bed regions (scene ranges in seconds) ---
    regions_street = [(0, 50.79), (94.76, 99.11)]      # street + city turn
    regions_room = [(28.95, 34.01), (57.43, 63.50)]    # corridor + stairwell
    regions_wind = [(50.79, 57.43), (63.50, 130.04)]   # building reveal + rooftop onward
    for a, b in regions_street:
        mono_to(bed_street, gen_city(b - a), a, 0.9)
    for a, b in regions_room:
        mono_to(bed_room, gen_room(b - a), a, 1.0)
    for a, b in regions_wind:
        mono_to(bed_wind, gen_wind(b - a), a, 0.55)

    # --- continuous low tension drone, swelling through the rooftop act ---
    t = np.arange(nframes(DUR)) / SR
    d = (sine(DUR, 48) * 0.5 + sine(DUR, 72) * 0.25)
    swell = 0.06 + 0.14 * np.clip((t - 63) / 30, 0, 1)
    swell *= (0.8 + 0.2 * np.sin(2 * math.pi * 0.05 * t))
    mono_to(drone, (d * swell).astype(np.float32), 0, 1.0)

    # --- footsteps: searching / montage / staircase run ---
    def walk(a, b, step=0.42, gain=0.5, run=False):
        tt = a
        i = 0
        while tt < b:
            place(fx, sfx_footstep(0.10 if run else 0.13), tt,
                  gain * (0.8 + 0.4 * rng.random()), pan=rng.uniform(-0.2, 0.2))
            tt += step * (0.85 if run else 1.0) * rng.uniform(0.92, 1.08)
            i += 1
    walk(13.0, 15.9, 0.5)                      # scene 1 decision steps
    walk(16.8, 23.6, 0.46)                     # six-hour search
    walk(24.2, 26.4, 0.5)                      # streetlight approach
    walk(34.4, 36.4, 0.55)                     # alley approach
    walk(57.7, 59.4, 0.28, gain=0.6, run=True) # stair run
    walk(63.7, 65.0, 0.5)                      # rooftop steps

    # --- anomaly glitch chirps (subtle, sparse) ---
    for at, pan in [(2.1, -0.4), (6.0, 0.5), (9.7, -0.3), (17.6, 0.3),
                    (20.4, -0.4), (27.4, 0.4), (30.6, 0.0), (44.9, 0.2),
                    (51.6, -0.2), (73.4, 0.3), (80.9, -0.3), (106.0, 0.2)]:
        place(fx, sfx_glitch(0.16), at, 0.32, pan)

    # --- scene transition digital tears ---
    for at in (16.36, 50.79, 57.43, 63.50, 109.80):
        place(fx, sfx_tear(0.2), at - 0.08, 0.4)

    # --- wall messages: scraping carve + dust ---
    place(fx, sfx_scrape(c(12)["end"] - c(12)["start"] + 0.4), c(12)["start"] - 0.1, 0.5)
    place(fx, sfx_pulse(0.4, 70), c(12)["end"], 0.4)        # confirmation thud
    place(fx, sfx_scrape(0.8), c(9)["start"], 0.22)

    # --- building materialization groan ---
    place(fx, sfx_rumble(2.2), 51.0, 0.5)
    place(fx, sfx_glitch(0.4, 1.4), 51.2, 0.3)

    # --- impossible staircase mechanical shifts ---
    place(fx, sfx_rumble(0.9), 59.13, 0.55)
    place(fx, sfx_tear(0.3), 59.13, 0.4)
    place(fx, sfx_rumble(0.9), 60.93, 0.55)
    place(fx, (sfx_clink() * 1.2).astype(np.float32), 61.2, 0.5)  # railing rattle

    # --- wrist zero reveal: activation + pulses + settle distortion ---
    place(fx, sfx_pulse(0.5, 420), c(20)["start"] + 1.2, 0.35)
    place(fx, sfx_pulse(0.25, 880), c(22)["start"], 0.28)
    place(fx, sfx_pulse(0.25, 880), c(22)["start"] + 0.4, 0.28)
    place(fx, sfx_glitch(0.3, 0.7), c(24)["start"], 0.4)

    # --- sky breaking apart ---
    place(fx, sfx_rumble(4.5), c(25)["start"], 0.6)
    for k in range(4):
        place(fx, sfx_crack(0.5), c(26)["start"] + 0.6 + k * 1.05, 0.4,
              pan=(-0.5 if k % 2 else 0.5))

    # --- "YOU do" restrained impact, timed to end of the phrase ---
    place(fx, sfx_drone_hit(1.8, 46), c(28)["end"] - 0.05, 0.7)

    # --- synchronized city turn: single mechanical click + sweep ---
    turn_at = c(29)["start"] + 0.55
    place(fx, sfx_pulse(0.35, 130), turn_at, 0.6)
    place(fx, bp(white(0.7), 200, 1600) * env(nframes(0.7), 0.05, 0.5) * 0.4,
          turn_at, 0.5, pan=0.0)

    # --- key transfer clink + resonant tone ---
    place(fx, sfx_clink(), c(30)["start"] + 1.0, 0.6)
    place(fx, sine(0.8, 660, 520) * env(nframes(0.8), 0.02, 0.7) * 0.2,
          c(30)["end"] - 0.6, 0.5)

    # --- warning phase-shift (brief stereo instability) ---
    place(fx, sfx_glitch(0.5, 0.6), c(32)["start"] + 0.8, 0.35, pan=0.6)

    # --- disappearance: interference + digital tear + low drop ---
    place(fx, sfx_glitch(0.4), c(33)["start"] + 0.2, 0.4)
    place(fx, sfx_tear(0.5), c(33)["start"] + 0.45, 0.5)
    place(fx, sfx_drone_hit(1.2, 38), c(33)["start"] + 0.7, 0.5)

    # --- choice card pulses + final glitch + clean ending ---
    place(fx, sfx_pulse(0.3, 520), c(36)["start"], 0.4)
    place(fx, sfx_pulse(0.3, 392), c(37)["start"], 0.4)
    place(fx, sfx_tear(0.3), DUR - 0.4, 0.45)

    # ----------------------------------------------------------------- stems
    np.save(os.path.join(OUT, "bed_street.npy"), bed_street)
    np.save(os.path.join(OUT, "bed_room.npy"), bed_room)
    np.save(os.path.join(OUT, "bed_wind.npy"), bed_wind)
    np.save(os.path.join(OUT, "fx.npy"), fx)
    np.save(os.path.join(OUT, "drone.npy"), drone)
    effects_mix = bed_street + bed_room + bed_wind + fx + drone
    # safety limiter on the effects bus
    peak = np.abs(effects_mix).max()
    if peak > 0.9: effects_mix *= 0.9 / peak
    np.save(os.path.join(OUT, "effects_mix.npy"), effects_mix.astype(np.float32))
    print("stems written to", OUT, "duration", round(DUR, 2), "s")

if __name__ == "__main__":
    main()
