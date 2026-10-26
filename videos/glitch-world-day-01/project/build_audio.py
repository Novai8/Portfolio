#!/usr/bin/env python3
"""
build_audio.py — the sound design + final mix.

Everything that is not the narration is synthesised here with numpy, so the
project carries no third-party audio and nothing needs licensing. The voiceover
stays the dominant element; effects sit 15-30 dB below it and are ducked under
speech.

    python3 project/build_audio.py

Outputs
    .work/mix.wav               48 kHz / 16-bit / stereo final mix
    assets/sound-effects/*.wav  the individual synthesised effects (reusable)
"""
from __future__ import annotations

import json
import math
import os
import wave

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SR = 48000
VO = os.path.join(ROOT, "audio", "original-voiceover.mp3")
SENT = os.path.join(ROOT, "scripts", "sentences.json")
ANALYSIS = os.path.join(ROOT, "scripts", "audio-analysis.json")
WORK = os.path.join(ROOT, ".work")
SFX_DIR = os.path.join(ROOT, "assets", "sound-effects")
OUT = os.path.join(WORK, "mix.wav")

rng = np.random.default_rng(7)


# ------------------------------------------------------------------ helpers ---
def t_axis(dur):
    return np.arange(int(dur * SR), dtype=np.float64) / SR


def env(dur, attack=0.005, decay=None, curve=3.0):
    n = int(dur * SR)
    e = np.ones(n)
    a = max(1, int(attack * SR))
    e[:a] = np.linspace(0, 1, a)
    if decay:
        d = max(1, int(decay * SR))
        d = min(d, n)
        e[-d:] *= np.linspace(1, 0, d) ** (1.0 / curve)
    return e


def sine(freq, dur, phase=0.0):
    t = t_axis(dur)
    if np.isscalar(freq):
        return np.sin(2 * np.pi * freq * t + phase)
    f = np.asarray(freq, dtype=np.float64)
    f = np.interp(np.linspace(0, 1, len(t)), np.linspace(0, 1, len(f)), f)
    return np.sin(2 * np.pi * np.cumsum(f) / SR + phase)


def noise(dur, color="white"):
    n = int(dur * SR)
    x = rng.normal(0, 1, n)
    if color == "pink":
        # simple one-pole filter bank approximation
        b = np.zeros(n)
        acc = 0.0
        for i in range(0, n, 1):
            acc = 0.98 * acc + 0.02 * x[i]
            b[i] = acc
        x = b / (np.max(np.abs(b)) + 1e-9)
    elif color == "brown":
        x = np.cumsum(x)
        x = x - np.linspace(x[0], x[-1], n)
        x /= (np.max(np.abs(x)) + 1e-9)
    return x


def lowpass(x, cutoff):
    """one-pole lowpass; cutoff may be a scalar or a per-sample array"""
    if np.isscalar(cutoff):
        a = math.exp(-2 * math.pi * float(cutoff) / SR)
        if a <= 0:
            return x.copy()
        k = int(math.ceil(math.log(1e-6) / math.log(a)))
        k = max(1, min(k, len(x)))
        ker = (1 - a) * a ** np.arange(k)
        return np.convolve(x, ker)[:len(x)]
    y = np.empty_like(x)
    acc = 0.0
    fc = np.asarray(cutoff, dtype=np.float64)
    for i in range(len(x)):
        a = math.exp(-2 * math.pi * fc[i] / SR)
        acc = (1 - a) * x[i] + a * acc
        y[i] = acc
    return y


def highpass(x, cutoff):
    return x - lowpass(x, cutoff)


def bitcrush(x, bits=4):
    q = 2 ** (bits - 1)
    return np.round(x * q) / q


def place(mix, clip, t, gain=1.0, pan=0.0):
    """additively place a mono clip into the stereo mix"""
    i = int(t * SR)
    if i >= mix.shape[0]:
        return
    n = min(len(clip), mix.shape[0] - i)
    if n <= 0:
        return
    l = math.sqrt(0.5 * (1 - pan))
    r = math.sqrt(0.5 * (1 + pan))
    mix[i:i + n, 0] += clip[:n] * gain * l
    mix[i:i + n, 1] += clip[:n] * gain * r


def save_wav(path, x, sr=SR):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    y = np.clip(x, -1, 1)
    if y.ndim == 1:
        y = np.stack([y, y], axis=1)
    data = (y * 32767).astype("<i2")
    with wave.open(path, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes(data.tobytes())


def load_voiceover():
    """decode the mp3 to 48k stereo float, preserving it exactly (no edits)"""
    from engine import ffmpeg_exe  # local helper
    import subprocess
    raw = os.path.join(WORK, "vo48.raw")
    subprocess.run([ffmpeg_exe(), "-y", "-hide_banner", "-loglevel", "error",
                    "-i", VO, "-ac", "2", "-ar", str(SR), "-f", "s16le", raw],
                   check=True)
    data = np.fromfile(raw, dtype="<i2").astype(np.float64) / 32768.0
    return data.reshape(-1, 2)


# -------------------------------------------------------------------- voices ---
def sfx_alarm(dur=2.4):
    x = np.zeros(int(dur * SR))
    for k in range(6):
        t0 = int(k * 0.36 * SR)
        beep = sine(1244, 0.14) * env(0.14, 0.004, 0.06)
        beep += 0.4 * sine(2488, 0.14) * env(0.14, 0.004, 0.06)
        n = min(len(beep), len(x) - t0)
        x[t0:t0 + n] += beep[:n]
    return x * env(dur, 0.01, 0.2)


def sfx_tick(dur=0.06):
    x = highpass(noise(dur), 2500) * env(dur, 0.001, 0.04, 6)
    x += 0.5 * sine(1800, dur) * env(dur, 0.001, 0.03, 8)
    return x * 0.5


def sfx_bird(dur=0.5):
    f = np.linspace(2600, 1700, int(dur * SR))
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) * env(dur, 0.01, 0.3, 2)
    x += 0.3 * np.sin(2 * np.pi * np.cumsum(f * 1.5) / SR) * env(dur, 0.01, 0.3, 2)
    return x * 0.5


def sfx_whoosh(dur=0.65):
    n = noise(dur, "pink")
    t = np.linspace(0, 1, len(n))
    band = lowpass(highpass(n, 300 + 900 * t), 1400 + 2600 * t)
    return band * (np.sin(np.pi * t) ** 1.5) * 0.8


def sfx_slam(dur=0.35):
    x = lowpass(noise(dur), 320) * env(dur, 0.001, 0.3, 2.4) * 1.2
    x += 0.7 * sine(70, dur) * env(dur, 0.001, 0.22, 2.0)
    return x


def sfx_system_error(dur=1.1):
    x = bitcrush(sine(340, dur) + 0.5 * sine(510, dur), 3) * 0.5
    x *= 0.4 + 0.6 * (np.sin(2 * np.pi * 7 * t_axis(dur)) > 0)
    x += 0.35 * highpass(noise(dur), 4000) * 0.25
    return x * env(dur, 0.004, 0.3)


def sfx_impact(dur=1.4):
    x = sine(np.array([120, 70, 45, 34]), dur) * env(dur, 0.002, 1.1, 2.2) * 1.3
    x += 0.5 * lowpass(noise(dur, "brown"), 240) * env(dur, 0.002, 0.9, 2.0)
    return x


def sfx_riser(dur=2.2):
    n = noise(dur, "pink")
    t = np.linspace(0, 1, len(n))
    x = lowpass(n, 400 + 5200 * t ** 2)
    x *= t ** 2.2
    x += 0.35 * sine(np.linspace(180, 900, len(n)), dur) * t ** 2.6 * 0.6
    return x


def sfx_glitch(dur=0.42):
    x = bitcrush(noise(dur), 2) * 0.5
    x *= (np.sin(2 * np.pi * 34 * t_axis(dur)) > 0.1)
    x += 0.3 * sine(np.array([1200, 300, 2000, 500]), dur) * 0.5
    return x * env(dur, 0.002, 0.25)


def sfx_cluck(dur=0.5):
    """rock -> chicken payoff"""
    out = np.zeros(int(dur * SR))
    for k, (tt, f0) in enumerate(((0.0, 520), (0.16, 700), (0.30, 430))):
        seg = np.zeros(int(0.12 * SR))
        f = np.linspace(f0, f0 * 1.8, len(seg))
        seg[:] = np.sin(2 * np.pi * np.cumsum(f) / SR)
        seg *= env(0.12, 0.002, 0.08, 2.5)
        i = int(tt * SR)
        n = min(len(seg), len(out) - i)
        out[i:i + n] += seg[:n]
    out += 0.25 * highpass(noise(dur), 3000) * env(dur, 0.01, 0.2)
    return out * 0.55


def sfx_pop(dur=0.18):
    return sine(np.linspace(900, 240, int(dur * SR)), dur) * env(dur, 0.001, 0.1, 2)


def sfx_ui(dur=0.25):
    x = sine(880, dur) * env(dur, 0.002, 0.2, 2) * 0.6
    x += sine(1320, dur) * env(dur, 0.002, 0.15, 2) * 0.25
    return x


def drone(dur, base=55.0, gain=1.0, wobble=0.15, bright=0.0):
    """continuous tension bed"""
    t = t_axis(dur)
    x = np.sin(2 * np.pi * base * t) * 0.5
    x += 0.32 * np.sin(2 * np.pi * base * 1.5 * t + 0.6)
    x += 0.20 * np.sin(2 * np.pi * base * 2.02 * t + 1.2)
    if bright:
        x += bright * 0.12 * np.sin(2 * np.pi * base * 6.0 * t)
    lfo = 1.0 + wobble * np.sin(2 * np.pi * 0.12 * t)
    x *= lfo * env(dur, 1.2, 1.5, 2.0)
    return x * gain


def heartbeat(dur=0.5):
    x = sine(58, dur) * env(dur, 0.004, 0.16, 2.0)
    x += 0.5 * sine(44, dur) * env(dur, 0.006, 0.24, 2.0)
    return x * 0.9


# ----------------------------------------------------------------------- mix ---
def duck_envelope(vo_mono, depth=0.45, smooth=0.08):
    """simple voice-activated duck: 1.0 when nobody speaks, 1-depth while talking"""
    hop = int(0.02 * SR)
    n = len(vo_mono) // hop
    e = np.array([np.sqrt(np.mean(vo_mono[i * hop:(i + 1) * hop] ** 2) + 1e-12)
                  for i in range(n)])
    db = 20 * np.log10(e + 1e-9)
    thr = np.percentile(db, 55) + 4
    active = (db > thr).astype(float)
    # smooth
    k = max(1, int(smooth / 0.02))
    ker = np.ones(k) / k
    active = np.convolve(active, ker, mode="same")
    act = np.interp(np.arange(len(vo_mono)) / hop, np.arange(n), active)
    return 1.0 - depth * np.clip(act, 0, 1)


def main():
    os.makedirs(WORK, exist_ok=True)
    os.makedirs(SFX_DIR, exist_ok=True)
    vo = load_voiceover()
    n = vo.shape[0]
    duration = n / SR
    print(f"voiceover: {duration:.3f}s @ {SR} Hz stereo")

    # voice: gentle high-pass, light compression, peak normalise to -1.5 dBFS
    mono = vo.mean(axis=1)
    hp = np.stack([highpass(vo[:, 0], 70), highpass(vo[:, 1], 70)], axis=1)
    env_ = np.abs(hp).max(axis=1)
    # smooth compressor
    k = int(0.05 * SR)
    ker = np.ones(k) / k
    env_s = np.convolve(env_, ker, mode="same")
    thr = 0.09
    gain = np.where(env_s > thr, (thr / np.maximum(env_s, 1e-6)) ** 0.35, 1.0)
    voice = hp * gain[:, None]
    voice *= (10 ** (-1.5 / 20)) / max(1e-9, np.abs(voice).max())

    # sfx bus + duck
    sfx = np.zeros((n, 2))
    duck = duck_envelope(mono)

    # ---- alarm + morning room tone ---------------------------------------
    save_wav(os.path.join(SFX_DIR, "alarm-clock.wav"), np.stack([sfx_alarm(), sfx_alarm()], axis=1))
    place(sfx, sfx_alarm(2.4), 0.10, gain=0.30, pan=-0.2)
    for k in range(int(3.2 / 0.52)):
        place(sfx, sfx_tick(), 0.35 + k * 0.52, gain=0.10, pan=0.35)
    # a whisper of room tone from the very first frame (and a soft power-on swell)
    room = noise(duration, "pink") * 0.012
    room *= np.clip(np.linspace(0, 1, len(room)) * 40, 0, 1)
    sfx[:, 0] += room
    sfx[:, 1] += room
    place(sfx, sine(np.linspace(90, 160, int(0.5 * SR)), 0.5) * env(0.5, 0.15, 0.25) * 0.12, 0.02,
          gain=0.5)

    # ---- the anomalies ----------------------------------------------------
    for k, tt in enumerate((6.2, 6.8, 7.4)):          # backward bird
        b = sfx_bird(0.5)
        place(sfx, b[::-1], tt, gain=0.16, pan=0.5)   # reversed chirp
    for k in range(7):                                 # rain going up
        place(sfx, highpass(noise(0.5), 5000) * 0.06 * env(0.5, 0.2, 0.3), 7.6 + k * 0.28,
              gain=0.5, pan=-0.4 + k * 0.12)
    place(sfx, sfx_pop(), 15.9, gain=0.14)             # "losing my mind" accent

    # ---- door: open -> ocean, slam, open -> store ------------------------
    place(sfx, sfx_whoosh(0.75), 18.5, gain=0.24)
    place(sfx, noise(2.2, "pink") * 0.5 * env(2.2, 0.6, 0.8, 2), 20.5, gain=0.10)  # ocean wash
    place(sfx, sfx_slam(), 23.0, gain=0.42)
    place(sfx, sfx_whoosh(0.6), 24.5, gain=0.22)
    place(sfx, sfx_ui(), 25.0, gain=0.10, pan=-0.3)
    place(sfx, sfx_ui(), 25.18, gain=0.08, pan=0.3)

    # ---- grocery store ----------------------------------------------------
    place(sfx, drone(9.0, base=110, gain=0.05, wobble=0.05), 28.2, gain=1.0)  # fridge hum
    place(sfx, sfx_pop(), 30.6, gain=0.18)             # "Even the milk."
    place(sfx, sfx_pop(), 31.0, gain=0.10)
    place(sfx, sfx_pop(), 37.0, gain=0.12)             # terrible decision

    # ---- reality update failed -------------------------------------------
    place(sfx, sfx_riser(2.6), 38.7, gain=0.26)
    place(sfx, sfx_system_error(1.2), 43.9, gain=0.30)
    place(sfx, sfx_system_error(1.0), 45.6, gain=0.22)
    place(sfx, sfx_impact(1.6), 44.0, gain=0.34)
    place(sfx, sfx_impact(1.4), 45.7, gain=0.26)
    place(sfx, sfx_impact(2.0), 47.6, gain=0.24)       # everyone freezes

    # ---- chicken ----------------------------------------------------------
    for k, tt in enumerate((51.2, 52.0, 52.7)):
        place(sfx, sfx_pop(), tt, gain=0.10, pan=-0.3)
    place(sfx, sfx_whoosh(0.35), 56.6, gain=0.18)      # the throw
    place(sfx, sfx_glitch(0.5), 59.1, gain=0.34)       # rock -> chicken
    place(sfx, sfx_cluck(0.6), 59.3, gain=0.30, pan=0.2)
    place(sfx, sfx_pop(), 60.6, gain=0.12)             # deadpan reaction

    # ---- celebration, then the stranger ---------------------------------
    place(sfx, sfx_ui(), 62.3, gain=0.10)
    place(sfx, sfx_ui(), 62.5, gain=0.08)
    place(sfx, drone(7.4, base=58, gain=0.16, wobble=0.2), 62.0, gain=1.0)
    place(sfx, sfx_riser(1.6), 67.6, gain=0.16)
    place(sfx, sfx_glitch(0.45), 69.4, gain=0.20)      # he turns
    place(sfx, sfx_ui(), 75.4, gain=0.16)              # pointing
    place(sfx, sfx_impact(0.9), 77.9, gain=0.20)       # "you're not real"
    place(sfx, sfx_glitch(0.7), 79.8, gain=0.38)       # he disappears
    place(sfx, sfx_glitch(0.4), 80.1, gain=0.22)

    # ---- countdown -------------------------------------------------------
    place(sfx, sfx_riser(1.4), 81.1, gain=0.20)
    place(sfx, sfx_impact(2.2), 82.4, gain=0.34)       # the timer lands
    place(sfx, drone(9.8, base=49, gain=0.20, wobble=0.22, bright=0.4), 81.0, gain=1.0)
    for k in range(9):
        place(sfx, sfx_tick(), 82.8 + k * 0.9, gain=0.055, pan=0.25)

    # ---- the choice ------------------------------------------------------
    place(sfx, drone(8.0, base=44, gain=0.22, wobble=0.25), 90.8, gain=1.0)
    place(sfx, sfx_ui(), 91.0, gain=0.12)
    place(sfx, sfx_ui(), 100.9, gain=0.16, pan=-0.4)   # option A card
    place(sfx, sfx_ui(), 105.4, gain=0.16, pan=0.4)    # option B card
    for k in range(9):
        place(sfx, heartbeat(), 101.2 + k * 0.95, gain=0.16)
    place(sfx, sfx_riser(2.2), 108.6, gain=0.16)
    place(sfx, sfx_impact(2.4), 110.3, gain=0.26)      # final line lands

    # apply ducking to the sfx bus, then mix
    sfx *= duck[:, None]
    mix = voice + sfx * 1.0

    # ---- master: fade, loudness to -14 LUFS, true-peak safe --------------
    fade = int(0.45 * SR)
    mix[-fade:] *= np.linspace(1, 0.07, fade)[:, None]   # settles, never hard-mutes
    target_lufs, tp_ceiling = -14.0, 10 ** (-1.5 / 20)
    try:
        import pyloudnorm as pyln
        meter = pyln.Meter(SR)
        loud = meter.integrated_loudness(mix)
        gain = 10 ** ((target_lufs - loud) / 20)
        mix *= gain
        # soft-knee limiter: tanh above 0.75 of the ceiling
        knee = tp_ceiling * 0.75
        a = np.abs(mix)
        over = a > knee
        if over.any():
            sign = np.sign(mix)
            mix = np.where(over, sign * (knee + (tp_ceiling - knee)
                                         * np.tanh((a - knee) / (tp_ceiling - knee))), mix)
        print(f"loudness {loud:6.2f} LUFS -> {target_lufs} LUFS (gain {20*math.log10(gain):+.2f} dB)")
    except Exception as exc:                                  # pragma: no cover
        print("loudness stage skipped:", exc)
        peak = np.abs(mix).max()
        if peak > 0.98:
            mix *= 0.98 / peak
    if np.abs(mix).max() > tp_ceiling:
        mix *= tp_ceiling / np.abs(mix).max()
    save_wav(OUT, mix)

    # stem report
    def rms_db(x):
        return 20 * math.log10(float(np.sqrt(np.mean(x ** 2))) + 1e-12)

    print(f"voice  rms {rms_db(voice):6.1f} dB   peak {20*math.log10(np.abs(voice).max()+1e-12):6.1f} dBFS")
    print(f"sfx    rms {rms_db(sfx*0.0 + sfx):6.1f} dB   (ducked, pre-mix)")
    print(f"mix    rms {rms_db(mix):6.1f} dB   peak {20*math.log10(np.abs(mix).max()+1e-12):6.1f} dBFS")
    print("wrote", OUT)


if __name__ == "__main__":
    main()
