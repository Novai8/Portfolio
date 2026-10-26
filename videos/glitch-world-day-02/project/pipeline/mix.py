#!/usr/bin/env python3
"""Combine narration with the synthesized effects bed (pre-loudnorm mix)."""
import json, os, wave
import numpy as np

SR = 48000
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
STEM = os.path.join(ROOT, "assets", "audio", "stems")
VO = os.path.join(ROOT, "assets", "audio", "source", "day-02-voiceover-48k.wav")

def read_wav(path):
    w = wave.open(path, "rb")
    assert w.getframerate() == SR, "narration must be 48 kHz"
    n = w.getnframes(); ch = w.getnchannels(); sw = w.getsampwidth()
    raw = w.readframes(n); w.close()
    x = np.frombuffer(raw, dtype={1: np.int8, 2: np.int16, 4: np.int32}[sw]).astype(np.float32)
    x = x / float(2 ** (8 * sw - 1))
    return x.reshape(-1, ch)

def main():
    timing = json.load(open(os.path.join(ROOT, "voiceover-timing.json")))
    dur = timing["measured_duration_s"]
    N = int(dur * SR)

    vo = read_wav(VO)
    if vo.shape[1] == 1:
        vo = np.repeat(vo, 2, axis=1)
    if len(vo) < N:
        vo = np.pad(vo, ((0, N - len(vo)), (0, 0)))
    vo = vo[:N].copy()

    fx = np.load(os.path.join(STEM, "effects_mix.npy"))[:N]
    if len(fx) < N:
        fx = np.pad(fx, ((0, N - len(fx)), (0, 0)))

    # sidechain ducking: dip the effects bed whenever narration is active.
    mono = vo.mean(axis=1)
    win = SR // 20  # 50 ms
    nblk = int(np.ceil(N / win))
    rms = np.zeros(nblk, np.float32)
    for i in range(nblk):
        seg = mono[i * win:(i + 1) * win]
        rms[i] = np.sqrt(np.mean(seg ** 2) + 1e-9)
    activity = np.clip((rms - 0.012) / 0.05, 0, 1)  # 0 silent .. 1 speech
    # smooth the control signal
    sm = np.empty_like(activity); prev = 0
    atk, rel = 0.25, 0.06
    for i, v in enumerate(activity):
        k = atk if v > prev else rel
        prev = prev + (v - prev) * k; sm[i] = prev
    gain = (1 - 0.45 * np.repeat(sm, win))[:N]
    fx = fx * gain[:, None]

    # keep the narration exactly as delivered; only set the effects level
    fx *= 0.85
    mix = vo + fx

    # soft safety limiter (headroom before the ffmpeg loudnorm/true-peak stage)
    peak = np.abs(mix).max()
    if peak > 0.95:
        mix *= 0.95 / peak
    mix = np.tanh(mix * 1.05) / np.tanh(1.05)

    out = os.path.join(ROOT, "assets", "audio", "day-02-mix-pre.wav")
    pcm = np.clip(mix, -1, 1)
    with wave.open(out, "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((pcm * 32767).astype(np.int16).tobytes())
    print("pre-mix written:", out, "peak", round(float(np.abs(mix).max()), 3))

if __name__ == "__main__":
    main()
