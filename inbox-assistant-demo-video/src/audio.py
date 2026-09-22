"""Procedural sound design: minimal electronic pulse music bed + modern UI SFX
palette (hover tick, click tok, short whoosh, soft pop, typing, amber caution,
success chime). Mixed voiceover-first. Outputs sfx.wav, music.wav."""
import numpy as np, wave, sys, os, math
sys.path.insert(0, os.path.dirname(__file__))
import beats as B

SR = 48000
DUR = 164.0
N = int(SR * DUR)
rng = np.random.default_rng(3)

def env_adsr(n, a, d, s_level, r, sr=SR):
    a_n, d_n, r_n = int(a * sr), int(d * sr), int(r * sr)
    s_n = max(0, n - a_n - d_n - r_n)
    e = np.concatenate([np.linspace(0, 1, a_n, endpoint=False),
                        np.linspace(1, s_level, d_n, endpoint=False),
                        np.full(s_n, s_level),
                        np.linspace(s_level, 0, r_n)])
    return e[:n] if len(e) >= n else np.pad(e, (0, n - len(e)))

def tone(f, n, kind="sine", sr=SR):
    t = np.arange(n) / sr
    if kind == "sine": return np.sin(2 * np.pi * f * t)
    if kind == "tri": return 2 / np.pi * np.arcsin(np.sin(2 * np.pi * f * t))
    if kind == "soft":  # sine + light 2nd harmonic
        return np.sin(2 * np.pi * f * t) + 0.25 * np.sin(4 * np.pi * f * t)
    return np.sin(2 * np.pi * f * t)

def lowpass(x, cutoff, sr=SR):
    from scipy.signal import butter, sosfilt
    sos = butter(2, cutoff / (sr / 2), btype="low", output="sos")
    return sosfilt(sos, x)

def bandpass(x, lo, hi, sr=SR):
    from scipy.signal import butter, sosfilt
    sos = butter(2, [lo / (sr / 2), hi / (sr / 2)], btype="band", output="sos")
    return sosfilt(sos, x)

# ---------------- SFX generators ----------------
def sfx_tick(f=3200):
    n = int(0.035 * SR)
    return tone(f, n) * env_adsr(n, 0.001, 0.02, 0.0, 0.01) * 0.5

def sfx_click():
    n = int(0.08 * SR)
    body = tone(1800, n) * env_adsr(n, 0.001, 0.03, 0.0, 0.02)
    thump = tone(190, n) * env_adsr(n, 0.001, 0.05, 0.0, 0.02) * 0.9
    noise = lowpass(rng.normal(0, 1, n), 4000) * env_adsr(n, 0.0005, 0.012, 0, 0.005) * 0.35
    return (body * 0.5 + thump + noise) * 0.7

def sfx_pop(f=480):
    n = int(0.14 * SR)
    t = np.arange(n) / SR
    fr = f * (1 + 0.6 * np.exp(-t * 60))       # quick downward pitch bend
    ph = 2 * np.pi * np.cumsum(fr) / SR
    x = np.sin(ph) * env_adsr(n, 0.002, 0.10, 0.0, 0.03)
    return x * 0.6

def sfx_whoosh(dur=0.13):
    n = int(dur * SR)
    nz = rng.normal(0, 1, n)
    t = np.linspace(0, 1, n)
    # sweep bandpass center up
    x = bandpass(nz, 500, 5000)
    e = np.sin(np.pi * t) ** 1.6
    return x * e * 0.35

def sfx_sweep():
    n = int(0.6 * SR)
    nz = rng.normal(0, 1, n)
    x = lowpass(nz, 1500)
    t = np.linspace(0, 1, n)
    return x * (np.sin(np.pi * t) ** 2) * 0.25

def sfx_roll(count=8, dur=0.7):
    out = np.zeros(int(dur * SR) + int(0.05 * SR))
    for i in range(count):
        p = i / count
        pos = int((p ** 1.6) * dur * SR)
        tk = sfx_tick(2600 + i * 80) * (0.5 + 0.5 * p)
        out[pos:pos + len(tk)] += tk
    return out

def sfx_typing(dur=2.0):
    n = int(dur * SR); out = np.zeros(n + SR // 5)
    t = 0.0
    while t < dur:
        pos = int(t * SR)
        k = int(0.03 * SR)
        key = lowpass(rng.normal(0, 1, k), 3500 + rng.uniform(-800, 800)) * env_adsr(k, 0.001, 0.02, 0, 0.005)
        out[pos:pos + k] += key * rng.uniform(0.18, 0.3)
        t += rng.uniform(0.045, 0.11)
    return out

def sfx_caution():
    n = int(0.55 * SR)
    a = tone(523, n, "soft") * env_adsr(n, 0.01, 0.2, 0.4, 0.3)
    b = tone(415, n, "soft") * env_adsr(n, 0.12, 0.2, 0.4, 0.25)
    return (a + b) * 0.28

def sfx_chime(notes):
    total = int((0.12 * len(notes) + 0.9) * SR)
    out = np.zeros(total)
    for i, f in enumerate(notes):
        n = int(0.9 * SR)
        x = tone(f, n, "soft") * env_adsr(n, 0.005, 0.3, 0.25, 0.5)
        pos = int(i * 0.11 * SR)
        out[pos:pos + n] += x * 0.28
    return out

GEN = {
    "tick": lambda p: sfx_tick(p.get("f", 3200)),
    "click": lambda p: sfx_click(),
    "pop": lambda p: sfx_pop(p.get("f", 480)),
    "whoosh": lambda p: sfx_whoosh(),
    "sweep": lambda p: sfx_sweep(),
    "roll": lambda p: sfx_roll(p.get("n", 8)),
    "typing": lambda p: sfx_typing(p.get("dur", 2.0)),
    "caution": lambda p: sfx_caution(),
    "chime": lambda p: sfx_chime(p.get("notes", [523, 784])),
}

def build_sfx(gain=1.0):
    out = np.zeros(N)
    for (t, kind, vol, p) in B.SFX:
        x = GEN[kind](p) * vol * gain
        pos = int(t * SR)
        end = min(N, pos + len(x))
        out[pos:end] += x[:end - pos]
    return out

# ---------------- music bed ----------------
def build_music():
    out = np.zeros(N)
    bpm = 96; beat = 60 / bpm
    # chord progression per section (root freqs), minimal pad + pulse
    sections = [(0, 53.18, [130.81, 146.83]),      # C, D warm-ish
                (53.18, 95.02, [146.83, 174.61]),  # D, F
                (95.02, 126.04, [164.81, 130.81]), # E, C
                (126.04, 164.0, [110.0, 130.81])]  # A, C
    t_all = np.arange(N) / SR
    # pad
    for a, b, roots in sections:
        i0, i1 = int(a * SR), int(b * SR)
        seg = np.zeros(i1 - i0); tt = np.arange(i1 - i0) / SR
        for k, r in enumerate(roots):
            for mult, amp in ((1, 0.5), (1.5, 0.25), (2, 0.3), (3, 0.08)):
                seg += amp * np.sin(2 * np.pi * r * mult * tt + k) * (0.5 + 0.5 * np.sin(2 * np.pi * 0.07 * tt + k * 2))
        seg = lowpass(seg, 900)
        fade = np.minimum(1, np.minimum(tt / 1.5, (b - a - tt) / 1.5))
        out[i0:i1] += seg * 0.09 * fade
    # pulse (soft sine pluck on 8ths, accent on beat)
    t = 0.0; i = 0
    while t < DUR - 1.5:
        n = int(0.16 * SR)
        f = 261.63 if i % 2 == 0 else 392.0
        if t >= 53.18: f *= 1.1225
        if t >= 126.04: f *= 0.8409
        amp = 0.22 if i % 4 == 0 else 0.11
        x = tone(f * 2, n, "sine") * env_adsr(n, 0.002, 0.12, 0, 0.03) * amp
        pos = int(t * SR); out[pos:pos + n] += x
        # sub kick on 1 and 3
        if i % 4 == 0:
            kn = int(0.18 * SR); kt = np.arange(kn) / SR
            kick = np.sin(2 * np.pi * (55 + 40 * np.exp(-kt * 30)) * kt) * env_adsr(kn, 0.001, 0.15, 0, 0.02)
            out[pos:pos + kn] += kick * 0.35
        t += beat / 2; i += 1
    # ducking during pivot & final resolve: fade out tail after 162.0
    tail = np.ones(N); i0 = int(161.9 * SR)
    tail[i0:] = np.linspace(1, 0, N - i0) ** 1.5
    tail[:int(0.8 * SR)] = np.linspace(0, 1, int(0.8 * SR))
    # final resolving chord
    n = int(2.4 * SR); pos = int(161.86 * SR)
    for f, a in ((130.81, 0.5), (196.0, 0.35), (261.63, 0.3), (329.63, 0.2)):
        x = tone(f, n, "soft") * env_adsr(n, 0.05, 0.6, 0.5, 1.6) * a
        m = min(n, N - pos); out[pos:pos + m] += x[:m] * 0.16
    return out * tail

def write_wav(path, x):
    x = np.clip(x, -1, 1)
    with wave.open(path, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((x * 32767).astype(np.int16).tobytes())

if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "."
    write_wav(os.path.join(out, "sfx.wav"), build_sfx())
    write_wav(os.path.join(out, "music.wav"), build_music())
    print("ok")
