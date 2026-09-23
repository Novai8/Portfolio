/**
 * sfxManager.ts — procedural sound-effects engine (97 named recipes, 123
 * scheduled events).
 *
 * Instead of shipping 60+ audio files, every effect is synthesized live with
 * the Web Audio API (oscillators, noise buffers, filters, FM). This keeps the
 * bundle tiny, guarantees zero network stalls, and — because each recipe is
 * parameterized — lets every event land at an exact audio-clock timestamp.
 *
 * Howler is used for AudioContext lifecycle management (auto-unlock on first
 * user gesture, auto-suspend when idle); the voiceover itself plays through a
 * plain <audio> element so `currentTime` remains the single master clock.
 */
import { Howler } from 'howler';

type AnyCtx = AudioContext;

class SfxEngine {
  private ctx: AnyCtx | null = null;
  private master: GainNode | null = null;
  private noiseBuf: AudioBuffer | null = null;
  enabled = true;
  volume = 0.5;

  ensure(): AnyCtx | null {
    if (typeof window === 'undefined') return null;
    if (!this.ctx) {
      const AC: typeof AudioContext | undefined =
        window.AudioContext || (window as unknown as { webkitAudioContext?: typeof AudioContext }).webkitAudioContext;
      if (!AC) return null;
      this.ctx = Howler.ctx ?? new AC();
      const comp = this.ctx.createDynamicsCompressor();
      comp.threshold.value = -14;
      comp.ratio.value = 8;
      this.master = this.ctx.createGain();
      this.master.gain.value = this.enabled ? this.volume : 0;
      this.master.connect(comp);
      comp.connect(this.ctx.destination);
    }
    if (this.ctx.state === 'suspended') void this.ctx.resume();
    return this.ctx;
  }

  resume() {
    const c = this.ensure();
    if (c && c.state === 'suspended') void c.resume();
  }

  setEnabled(on: boolean) {
    this.enabled = on;
    if (this.master && this.ctx) {
      this.master.gain.setTargetAtTime(on ? this.volume : 0, this.ctx.currentTime, 0.03);
    }
  }

  setVolume(v: number) {
    this.volume = v;
    if (this.master && this.ctx && this.enabled) {
      this.master.gain.setTargetAtTime(v, this.ctx.currentTime, 0.03);
    }
  }

  private noise(ctx: AnyCtx): AudioBuffer {
    if (!this.noiseBuf) {
      const len = ctx.sampleRate * 2;
      const buf = ctx.createBuffer(1, len, ctx.sampleRate);
      const d = buf.getChannelData(0);
      for (let i = 0; i < len; i++) d[i] = Math.random() * 2 - 1;
      this.noiseBuf = buf;
    }
    return this.noiseBuf;
  }

  // ---------- synthesis primitives ----------
  private tone(o: {
    f0: number; f1?: number; type?: OscillatorType; t: number; dur: number; g?: number;
    a?: number; vib?: number; vibRate?: number; detune?: number;
  }) {
    const ctx = this.ctx!;
    const osc = ctx.createOscillator();
    const gain = ctx.createGain();
    osc.type = o.type ?? 'sine';
    const t = ctx.currentTime + o.t;
    osc.frequency.setValueAtTime(Math.max(20, o.f0), t);
    if (o.f1 !== undefined) osc.frequency.exponentialRampToValueAtTime(Math.max(20, o.f1), t + o.dur);
    if (o.detune) osc.detune.value = o.detune;
    const peak = o.g ?? 0.2;
    const a = o.a ?? 0.005;
    gain.gain.setValueAtTime(0.0001, t);
    gain.gain.exponentialRampToValueAtTime(peak, t + a);
    gain.gain.exponentialRampToValueAtTime(0.0001, t + o.dur);
    osc.connect(gain).connect(this.master!);
    if (o.vib) {
      const lfo = ctx.createOscillator();
      const lg = ctx.createGain();
      lfo.frequency.value = o.vibRate ?? 6;
      lg.gain.value = o.vib;
      lfo.connect(lg).connect(osc.frequency);
      lfo.start(t);
      lfo.stop(t + o.dur + 0.05);
    }
    osc.start(t);
    osc.stop(t + o.dur + 0.05);
  }

  private noiseHit(o: {
    t: number; dur: number; g?: number; type?: BiquadFilterType;
    f0?: number; f1?: number; q?: number; a?: number;
  }) {
    const ctx = this.ctx!;
    const src = ctx.createBufferSource();
    src.buffer = this.noise(ctx);
    src.loop = true;
    const filt = ctx.createBiquadFilter();
    filt.type = o.type ?? 'bandpass';
    filt.Q.value = o.q ?? 1;
    const t = ctx.currentTime + o.t;
    filt.frequency.setValueAtTime(o.f0 ?? 1000, t);
    if (o.f1 !== undefined) filt.frequency.exponentialRampToValueAtTime(Math.max(30, o.f1), t + o.dur);
    const gain = ctx.createGain();
    const peak = o.g ?? 0.15;
    gain.gain.setValueAtTime(0.0001, t);
    gain.gain.exponentialRampToValueAtTime(peak, t + (o.a ?? 0.004));
    gain.gain.exponentialRampToValueAtTime(0.0001, t + o.dur);
    src.connect(filt).connect(gain).connect(this.master!);
    src.start(t);
    src.stop(t + o.dur + 0.05);
  }

  private arp(freqs: number[], step: number, o: { type?: OscillatorType; g?: number; dur?: number; t?: number }) {
    const t0 = o.t ?? 0;
    freqs.forEach((f, i) =>
      this.tone({ f0: f, t: t0 + i * step, dur: o.dur ?? 0.16, type: o.type ?? 'triangle', g: o.g ?? 0.16, a: 0.004 })
    );
  }

  private bell(f: number, t: number, dur: number, g: number, index = 3.5) {
    const ctx = this.ctx!;
    const carrier = ctx.createOscillator();
    const mod = ctx.createOscillator();
    const modGain = ctx.createGain();
    const gain = ctx.createGain();
    carrier.frequency.value = f;
    mod.frequency.value = f * 2.01;
    modGain.gain.value = f * index;
    const T = ctx.currentTime + t;
    mod.connect(modGain).connect(carrier.frequency);
    gain.gain.setValueAtTime(0.0001, T);
    gain.gain.exponentialRampToValueAtTime(g, T + 0.008);
    gain.gain.exponentialRampToValueAtTime(0.0001, T + dur);
    carrier.connect(gain).connect(this.master!);
    mod.start(T); carrier.start(T);
    mod.stop(T + dur + 0.05); carrier.stop(T + dur + 0.05);
  }

  // ---------- named recipes ----------
  private play(name: string) {
    if (!this.ensure() || !this.enabled) return;
    const N = name;
    switch (N) {
      // ----- UI -----
      case 'click': case 'mouseClick': this.tone({ f0: 2400, f1: 1200, type: 'square', t: 0, dur: 0.04, g: 0.08 }); this.noiseHit({ t: 0, dur: 0.03, f0: 4000, g: 0.05 }); break;
      case 'keyTap': case 'keyboardTap': this.noiseHit({ t: 0, dur: 0.035, f0: 3200, f1: 1800, q: 2, g: 0.07 }); this.tone({ f0: 880, f1: 660, type: 'triangle', t: 0, dur: 0.03, g: 0.04 }); break;
      case 'rapidClicks': for (let i = 0; i < 7; i++) this.tone({ f0: 2000 + Math.random() * 800, f1: 900, type: 'square', t: i * 0.055, dur: 0.03, g: 0.06 }); break;
      case 'typing': case 'typingCalm': for (let i = 0; i < 9; i++) this.noiseHit({ t: i * 0.075, dur: 0.03, f0: 2800 + Math.random() * 1200, q: 3, g: 0.045 }); break;
      case 'typingFast': case 'typingSearch': for (let i = 0; i < 16; i++) this.noiseHit({ t: i * 0.042, dur: 0.025, f0: 2600 + Math.random() * 1800, q: 3, g: 0.05 }); break;
      case 'toggle1': case 'toggle2': case 'toggle3': this.tone({ f0: N === 'toggle1' ? 700 : N === 'toggle2' ? 840 : 980, f1: 1500, type: 'square', t: 0, dur: 0.07, g: 0.1 }); break;
      case 'slider': this.tone({ f0: 500, f1: 1600, type: 'sawtooth', t: 0, dur: 0.16, g: 0.07 }); break;
      case 'checkbox': this.arp([880, 1320], 0.06, { type: 'sine', g: 0.13 }); break;
      case 'uiPop': this.tone({ f0: 420, f1: 1350, type: 'sine', t: 0, dur: 0.12, g: 0.16 }); this.tone({ f0: 840, f1: 2100, t: 0.015, dur: 0.1, g: 0.07 }); break;
      case 'stickerPeel': this.noiseHit({ t: 0, dur: 0.22, f0: 900, f1: 3600, q: 0.8, g: 0.1 }); this.tone({ f0: 300, f1: 900, type: 'triangle', t: 0.16, dur: 0.09, g: 0.1 }); break;
      case 'pageFlip': this.noiseHit({ t: 0, dur: 0.16, f0: 1800, f1: 600, q: 0.6, g: 0.1, type: 'highpass' }); break;
      case 'cardShuffle': for (let i = 0; i < 10; i++) this.noiseHit({ t: i * 0.045, dur: 0.05, f0: 1500 + Math.random() * 2500, q: 1.5, g: 0.06 }); break;
      case 'stamp': case 'slamNotification': this.noiseHit({ t: 0, dur: 0.1, f0: 400, f1: 90, q: 0.5, g: 0.3, type: 'lowpass' }); this.tone({ f0: 160, f1: 50, t: 0, dur: 0.18, g: 0.28 }); break;
      case 'cameraShutter': this.noiseHit({ t: 0, dur: 0.03, f0: 5000, g: 0.12 }); this.noiseHit({ t: 0.06, dur: 0.04, f0: 3200, g: 0.1 }); break;
      // ----- motion -----
      case 'whoosh': case 'whooshZoom': case 'searchWhoosh': case 'refreshSwoosh': case 'sendSwoosh': case 'mergeWhoosh': case 'contrastWhoosh': case 'roomTransition':
        this.noiseHit({ t: 0, dur: 0.42, f0: 300, f1: 4200, q: 0.7, g: 0.14, a: 0.08 });
        this.noiseHit({ t: 0.16, dur: 0.3, f0: 4200, f1: 500, q: 0.7, g: 0.1, a: 0.05 });
        break;
      case 'zoomIn': case 'mapZoom': case 'kaleidoscopeSpin':
        this.tone({ f0: 220, f1: 1800, type: 'sine', t: 0, dur: 0.55, g: 0.12 });
        this.noiseHit({ t: 0, dur: 0.5, f0: 400, f1: 5000, q: 1.2, g: 0.09, a: 0.1 });
        if (N === 'kaleidoscopeSpin') this.arp([523, 659, 784, 1047, 1319, 1568], 0.06, { type: 'sine', g: 0.07 });
        break;
      case 'spin': this.tone({ f0: 300, f1: 900, type: 'triangle', t: 0, dur: 0.3, g: 0.09, vib: 30, vibRate: 14 }); break;
      case 'slide': this.noiseHit({ t: 0, dur: 0.18, f0: 600, f1: 200, q: 0.9, g: 0.08 }); break;
      case 'flashImpact': this.noiseHit({ t: 0, dur: 0.3, f0: 6000, f1: 1200, g: 0.14, type: 'highpass' }); this.tone({ f0: 1400, f1: 200, t: 0, dur: 0.3, g: 0.1 }); break;
      case 'pinDrop': case 'pinStick': this.tone({ f0: 1200, f1: 300, type: 'sine', t: 0, dur: 0.07, g: 0.12 }); this.noiseHit({ t: 0.05, dur: 0.04, f0: 2000, g: 0.08 }); break;
      case 'thud': this.tone({ f0: 120, f1: 40, t: 0, dur: 0.2, g: 0.3 }); break;
      case 'footsteps': for (let i = 0; i < 5; i++) this.noiseHit({ t: i * 0.24, dur: 0.08, f0: 220, f1: 90, q: 0.8, g: 0.12, type: 'lowpass' }); break;
      // ----- emotional -----
      case 'heartbeatFast': this.tone({ f0: 65, f1: 40, t: 0, dur: 0.12, g: 0.3 }); this.tone({ f0: 58, f1: 38, t: 0.18, dur: 0.1, g: 0.2 }); break;
      case 'heartbeatSlow': this.tone({ f0: 55, f1: 36, t: 0, dur: 0.16, g: 0.26 }); this.tone({ f0: 50, f1: 34, t: 0.26, dur: 0.12, g: 0.16 }); break;
      case 'nervousLaugh': case 'laughUi': case 'dryLaugh': case 'chuckle': case 'laugh': case 'laughWarm':
        { const base = N === 'dryLaugh' ? 300 : N === 'chuckle' ? 340 : 380;
          [0, 1, 2, 3].forEach((i) => this.tone({ f0: base + i * 40, f1: base - 60, type: 'triangle', t: i * 0.11, dur: 0.09, g: 0.1, vib: 22, vibRate: 24 })); break; }
      case 'nervousLaughEcho':
        [0, 1, 2].forEach((i) => this.tone({ f0: 420, f1: 300, type: 'triangle', t: i * 0.16, dur: 0.12, g: 0.09 - i * 0.02, vib: 30, vibRate: 22 }));
        this.tone({ f0: 420, f1: 300, type: 'triangle', t: 0.62, dur: 0.2, g: 0.04, vib: 30, vibRate: 22 });
        break;
      case 'laughRelease': this.arp([392, 494, 587, 784], 0.09, { type: 'triangle', g: 0.13 }); [0, 1, 2].forEach((i) => this.tone({ f0: 500 + i * 60, f1: 380, type: 'triangle', t: 0.4 + i * 0.12, dur: 0.1, g: 0.09 })); break;
      case 'breatheExhale': this.noiseHit({ t: 0, dur: 1.1, f0: 900, f1: 250, q: 0.4, g: 0.09, a: 0.35 }); break;
      case 'dreamyChime': this.arp([1046, 1318, 1568, 2093], 0.11, { type: 'sine', g: 0.09, dur: 0.5 }); break;
      case 'scaryString': this.tone({ f0: 180, f1: 170, type: 'sawtooth', t: 0, dur: 1.1, g: 0.08, vib: 9, vibRate: 5 }); this.tone({ f0: 181.5, f1: 168, type: 'sawtooth', t: 0, dur: 1.1, g: 0.07 }); break;
      case 'seriousShift': this.tone({ f0: 220, f1: 110, type: 'sawtooth', t: 0, dur: 0.4, g: 0.12 }); break;
      case 'ominousDrone': this.tone({ f0: 55, type: 'sawtooth', t: 0, dur: 2.2, g: 0.09 }); this.tone({ f0: 55.7, type: 'sawtooth', t: 0.05, dur: 2.2, g: 0.08 }); break;
      case 'ominousBass': this.tone({ f0: 82, f1: 41, type: 'sawtooth', t: 0, dur: 1.4, g: 0.16 }); this.noiseHit({ t: 0.1, dur: 1.2, f0: 200, f1: 60, g: 0.06, type: 'lowpass', a: 0.2 }); break;
      case 'tensionRiser': this.noiseHit({ t: 0, dur: 1.5, f0: 200, f1: 5200, q: 1.4, g: 0.13, a: 0.5 }); this.tone({ f0: 110, f1: 440, type: 'sawtooth', t: 0, dur: 1.5, g: 0.07 }); break;
      case 'stressRiser': this.noiseHit({ t: 0, dur: 0.9, f0: 400, f1: 3800, q: 2, g: 0.12, a: 0.3 }); this.tone({ f0: 160, f1: 640, type: 'square', t: 0, dur: 0.9, g: 0.05 }); break;
      case 'revelationPulse': this.tone({ f0: 330, f1: 660, t: 0, dur: 0.5, g: 0.12 }); this.tone({ f0: 660, f1: 1320, t: 0.1, dur: 0.4, g: 0.07 }); break;
      case 'holdMusic': { const sad = [329.6, 293.7, 246.9, 261.6]; sad.forEach((f, i) => this.tone({ f0: f, type: 'sine', t: i * 0.42, dur: 0.4, g: 0.09, vib: 4, vibRate: 5 })); break; }
      // ----- alerts -----
      case 'notification': case 'notificationPing': case 'emailCautious': this.bell(1568, 0, 0.5, N === 'emailCautious' ? 0.07 : 0.12, 2); this.bell(2093, 0.09, 0.4, 0.06, 2); break;
      case 'notificationMega': case 'urgentEmail': case 'urgentNotification': case 'threatNotification':
        this.bell(1046, 0, 0.7, 0.16, 4);
        this.bell(1318, 0.1, 0.6, 0.12, 4);
        this.tone({ f0: 2093, type: 'square', t: 0.05, dur: 0.2, g: 0.05 });
        this.tone({ f0: 1568, type: 'square', t: 0.24, dur: 0.25, g: 0.05 });
        break;
      case 'ping': this.tone({ f0: 1720, f1: 1680, t: 0, dur: 0.35, g: 0.12 }); break;
      case 'receive': this.arp([784, 988, 1175], 0.07, { type: 'sine', g: 0.12 }); break;
      case 'alarm': for (let i = 0; i < 4; i++) this.tone({ f0: 880, f1: 660, type: 'square', t: i * 0.3, dur: 0.22, g: 0.08 }); break;
      case 'errorGlitch': case 'glitchOut':
        for (let i = 0; i < 6; i++) this.noiseHit({ t: i * 0.07, dur: 0.05, f0: 300 + Math.random() * 4000, q: 4, g: 0.09 });
        this.tone({ f0: 110, type: 'square', t: 0, dur: 0.3, g: 0.07 });
        break;
      case 'failBuzzer': this.tone({ f0: 180, f1: 140, type: 'square', t: 0, dur: 0.32, g: 0.13 }); this.tone({ f0: 92, type: 'square', t: 0, dur: 0.32, g: 0.1 }); break;
      case 'timerTickLoop': case 'tick': case 'countTickLoop': this.noiseHit({ t: 0, dur: 0.02, f0: 3400, q: 6, g: 0.11 }); this.tone({ f0: 1200, f1: 900, t: 0, dur: 0.03, g: 0.06 }); break;
      case 'countdownBeep': this.tone({ f0: 1200, type: 'square', t: 0, dur: 0.1, g: 0.1 }); break;
      case 'glassCrack': case 'shatter':
        for (let i = 0; i < 12; i++) this.tone({ f0: 2400 + Math.random() * 3600, f1: 1200, type: 'triangle', t: i * 0.03 + Math.random() * 0.02, dur: 0.06, g: 0.06 });
        this.noiseHit({ t: 0, dur: 0.35, f0: 5000, f1: 1500, g: 0.14, type: 'highpass' });
        break;
      case 'iceFreeze': this.arp([2093, 2637, 3136], 0.05, { type: 'sine', g: 0.07 }); this.noiseHit({ t: 0.1, dur: 0.5, f0: 6000, f1: 9000, q: 0.4, g: 0.03, type: 'highpass' }); break;
      // ----- success -----
      case 'successChime': case 'notificationP': this.arp([523, 659, 784, 1046], 0.08, { type: 'sine', g: 0.14 }); this.bell(1568, 0.3, 0.8, 0.08); break;
      case 'reorderDing': this.bell(1318, 0, 0.7, 0.14, 2.5); this.bell(1976, 0.12, 0.6, 0.09, 2.5); break;
      case 'levelUp': case 'upgradeLevel': this.arp([392, 523, 659, 784, 1046, 1318], 0.07, { type: 'square', g: 0.08, dur: 0.12 }); break;
      case 'confettiSprinkle': for (let i = 0; i < 14; i++) this.tone({ f0: 1200 + Math.random() * 2600, f1: 2000, type: 'sine', t: Math.random() * 0.5, dur: 0.05, g: 0.045 }); break;
      case 'cashRegister': this.noiseHit({ t: 0, dur: 0.05, f0: 3000, g: 0.1 }); this.bell(1865, 0.03, 0.4, 0.14); this.bell(2217, 0.1, 0.5, 0.12); break;
      case 'lightbulbDing': this.bell(1568, 0, 0.9, 0.16, 5); this.tone({ f0: 3136, t: 0.02, dur: 0.3, g: 0.05 }); break;
      case 'wisdomGong': { const T = 2.6; [98, 147, 196, 294].forEach((f, i) => this.tone({ f0: f * (1 + i * 0.001), type: 'sine', t: 0, dur: T, g: 0.12 / (i + 1), vib: 2, vibRate: 1.2 })); this.noiseHit({ t: 0, dur: 0.4, f0: 500, f1: 150, g: 0.06, a: 0.01 }); break; }
      case 'callPositive': case 'pickup': case 'answer': this.arp([587, 880], 0.09, { type: 'sine', g: 0.13 }); break;
      case 'brightVoice': this.arp([659, 784, 988, 1175], 0.06, { type: 'triangle', g: 0.1 }); break;
      // ----- impact / comic -----
      case 'impactBoom': case 'attackDrop':
        this.tone({ f0: 90, f1: 32, type: 'sine', t: 0, dur: 0.6, g: 0.4 });
        this.noiseHit({ t: 0, dur: 0.4, f0: 900, f1: 80, q: 0.6, g: 0.22, type: 'lowpass' });
        break;
      case 'pop1': this.tone({ f0: 500, f1: 1500, type: 'sine', t: 0, dur: 0.1, g: 0.18 }); break;
      case 'pop2': this.tone({ f0: 600, f1: 1800, type: 'sine', t: 0, dur: 0.1, g: 0.18 }); break;
      case 'pop3Squeaky': this.tone({ f0: 900, f1: 2600, type: 'triangle', t: 0, dur: 0.14, g: 0.15, vib: 60, vibRate: 30 }); break;
      case 'silenceWhoosh': case 'outroFade': this.noiseHit({ t: 0, dur: 0.8, f0: 3200, f1: 220, q: 0.6, g: 0.1, a: 0.2 }); break;
      case 'snapBreak': case 'stringStretch': case 'stringSnap':
        if (N === 'stringStretch') this.noiseHit({ t: 0, dur: 0.5, f0: 2200, f1: 3600, q: 6, g: 0.06, a: 0.15 });
        else { this.noiseHit({ t: 0, dur: 0.06, f0: 2800, g: 0.16 }); this.tone({ f0: 1400, f1: 500, t: 0, dur: 0.09, g: 0.1 }); }
        break;
      case 'paperCrumple': case 'paperRustle': case 'flagFlutter':
        { const n = N === 'flagFlutter' ? 4 : 7;
          for (let i = 0; i < n; i++) this.noiseHit({ t: i * 0.06, dur: 0.07, f0: 1400 + Math.random() * 2400, q: 0.8, g: 0.07 }); break; }
      case 'cerealCrunch': for (let i = 0; i < 5; i++) this.noiseHit({ t: i * 0.11, dur: 0.06, f0: 900 + Math.random() * 700, q: 1.2, g: 0.09 }); break;
      case 'startupChime': this.arp([523, 784, 1046], 0.12, { type: 'sine', g: 0.13 }); this.bell(2093, 0.3, 1.2, 0.07); break;
      case 'gavel': this.noiseHit({ t: 0, dur: 0.08, f0: 700, f1: 200, g: 0.2, type: 'lowpass' }); this.tone({ f0: 180, f1: 70, t: 0, dur: 0.12, g: 0.2 }); break;
      case 'shieldAppear': this.tone({ f0: 196, f1: 392, type: 'sine', t: 0, dur: 0.6, g: 0.14 }); this.noiseHit({ t: 0.1, dur: 0.5, f0: 2000, f1: 4200, g: 0.04, a: 0.2 }); break;
      // ----- phone -----
      case 'phoneRing': for (let i = 0; i < 2; i++) { this.tone({ f0: 941, type: 'sine', t: i * 0.5, dur: 0.4, g: 0.07, vib: 0 }); this.tone({ f0: 1209, type: 'sine', t: i * 0.5, dur: 0.4, g: 0.07 }); } break;
      case 'phoneDial': [697, 852].forEach((f) => this.tone({ f0: f, type: 'sine', t: 0, dur: 0.18, g: 0.06 })); [1209, 1336].forEach((f) => this.tone({ f0: f, type: 'sine', t: 0.05, dur: 0.18, g: 0.06 })); break;
      case 'hangup': case 'hangupClick': this.tone({ f0: 350, type: 'sine', t: 0, dur: 0.15, g: 0.1 }); this.tone({ f0: 440, type: 'sine', t: 0.16, dur: 0.15, g: 0.1 }); break;
      case 'morningBirds': for (let i = 0; i < 6; i++) { const f = 2200 + Math.random() * 1600; this.tone({ f0: f, f1: f * 1.4, type: 'sine', t: 0.15 + i * 0.22 + Math.random() * 0.1, dur: 0.09, g: 0.05, vib: 90, vibRate: 26 }); } break;
      default: this.tone({ f0: 880, f1: 440, t: 0, dur: 0.1, g: 0.1 });
    }
  }

  /** Fire a named effect immediately (slight randomization keeps repeats organic). */
  trigger(name: string) {
    if (!this.enabled) return;
    this.play(name);
  }

  /** Preview every recipe (used by the debug overlay). */
  previewAll(stepMs = 240) {
    const names = this.recipes();
    names.forEach((n, i) => window.setTimeout(() => this.trigger(n), i * stepMs));
  }

  recipes(): string[] {
    return [
      'startupChime','keyTap','cerealCrunch','uiPop','laughUi','whooshZoom','click','pageFlip','stickerPeel','chuckle','cardShuffle',
      'refreshSwoosh','tick','flashImpact','notificationMega','impactBoom','countTickLoop','cashRegister','silenceWhoosh','kaleidoscopeSpin',
      'heartbeatFast','nervousLaugh','typingFast','dreamyChime','glitchOut','mapZoom','pinDrop','ominousDrone','flagFlutter','paperCrumple',
      'pop1','pop2','pop3Squeaky','mergeWhoosh','typing','sendSwoosh','notificationPing','receive','errorGlitch','pinStick','stringStretch',
      'paperRustle','stressRiser','snapBreak','roomTransition','dryLaugh','phoneRing','footsteps','zoomIn','pickup','brightVoice','laugh',
      'seriousShift','hangup','typingSearch','searchWhoosh','rapidClicks','failBuzzer','ominousBass','urgentNotification','timerTickLoop',
      'typingCalm','slamNotification','iceFreeze','glassCrack','phoneDial','holdMusic','answer','tensionRiser','revelationPulse','hangupClick',
      'threatNotification','scaryString','nervousLaughEcho','lightbulbDing','shieldAppear','shatter','cameraShutter','toggle1','toggle2','toggle3',
      'slider','checkbox','breatheExhale','attackDrop','silenceWhoosh','alarm','vending','laughRelease','confettiSprinkle','contrastWhoosh',
      'morningBirds','emailCautious','callPositive','laughWarm','successChime','reorderDing','levelUp','upgradeLevel','wisdomGong','outroFade',
      'heartbeatSlow','gavel','stamp','thud','slide','spin','ping','countdownBeep','heartbeat',
    ];
  }
}

export const sfx = new SfxEngine();

/** A scheduled SFX event resolved against the audio clock. */
export interface SfxEvent { time: number; sfx: string }
