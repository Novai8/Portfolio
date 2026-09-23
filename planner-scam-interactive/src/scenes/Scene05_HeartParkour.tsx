import { useEffect, useRef } from 'react';
import { SceneProps, SyncLine, PopWords, Reveal, anchorLocal } from './kit';
import { beat, clamp, hash } from '../lib/animationHelpers';

/**
 * SCENE 05 — "Heart Parkour"  (medical-monitor aesthetic)
 * Live EKG canvas, a heart doing parkour across platforms, split-screen
 * order details vs internal panic, lumbar-support dream cloud, flatline glitch.
 */
export function Scene05({ active, local, chunkIdx, wordIdx }: SceneProps & { chunkIdx: number }) {
  if (!active) return <div className="scene-inner" />;
  const aParkour = anchorLocal(5, 'parkour');
  const aWifi = anchorLocal(5, 'wifi');
  const aChair = anchorLocal(5, 'chair');
  const aElliot = anchorLocal(5, 'elliot');
  const aCleared = anchorLocal(5, 'cleared');
  const end = 22.9;
  const flat = beat(local, end - 1.4, 0.7);
  const glitch = beat(local, end - 0.6, 0.6);

  return (
    <div className="scene-inner">
      <Ekg local={local} flat={flat > 0} />

      {/* heart parkour */}
      <HeartParkour local={local} start={aParkour} glitch={glitch} />

      {/* split screen cards */}
      <Reveal at={aElliot - 0.3} local={local} rise={36} style={{ position: 'absolute', left: 90, top: 150 }}>
        <div className="card" style={{ width: 470, padding: '24px 30px', borderColor: 'rgba(0,255,136,0.35)' }}>
          <div style={{ fontFamily: 'var(--font-mono)', fontSize: 13, letterSpacing: '0.25em', color: '#39ff88' }}>ORDER DETAILS · COLD FACTS</div>
          <div style={{ marginTop: 12, display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 10, color: '#cfe9dd', fontSize: 19, fontWeight: 600 }}>
            <div>🧾 Planners <b style={{ color: '#fff' }}>500</b></div>
            <div>💵 Total <b style={{ color: '#00ff88' }}>$12,480</b></div>
            <div>👤 Customer <b style={{ color: '#fff' }}>“Elliot Graye”</b></div>
            <div>📧 Email <b style={{ color: '#fff' }}>looks legit</b></div>
          </div>
        </div>
      </Reveal>

      <Reveal at={aElliot + 0.4} local={local} rise={36} style={{ position: 'absolute', right: 90, top: 170 }}>
        <div className="card" style={{ width: 430, padding: '24px 30px', borderColor: 'rgba(255,0,110,0.5)', background: 'rgba(60,6,26,0.55)' }}>
          <div style={{ fontFamily: 'var(--font-mono)', fontSize: 13, letterSpacing: '0.25em', color: '#ff5c8a' }}>INTERNAL MONOLOGUE · PANIC</div>
          <div style={{ marginTop: 12, color: '#ffd6e9', fontFamily: 'var(--font-hand)', fontSize: 30, lineHeight: 1.3 }}>
            “a person with Wi‑Fi and a dream” 🫠
          </div>
          <div style={{ marginTop: 10, display: 'flex', gap: 8 }}>
            {[...Array(12)].map((_, i) => (
              <span key={i} style={{ width: 4, height: 10 + hash(i) * 34, background: '#ff006e', opacity: 0.5 + 0.5 * Math.sin(local * 8 + i), borderRadius: 2 }} />
            ))}
          </div>
        </div>
      </Reveal>

      {/* dream sequence */}
      {local > aChair - 0.7 && (
        <div
          style={{
            position: 'absolute', left: '50%', top: 130, transform: `translateX(-50%) translateY(${-10 * Math.sin(local * 1.6)}px)`,
            opacity: clamp(1 - Math.max(0, flat)),
            textAlign: 'center',
          }}
        >
          <div
            style={{
              background: 'radial-gradient(60% 90% at 50% 40%, rgba(255,215,130,0.28), transparent 70%)',
              borderRadius: 200, padding: '34px 70px',
              animation: 'floaty-soft 3s ease-in-out infinite',
            }}
          >
            <div style={{ fontSize: 110, filter: 'drop-shadow(0 0 44px rgba(255,215,130,0.8))' }}>🪑</div>
            <div style={{ fontFamily: 'var(--font-display)', fontSize: 36, color: '#ffe9b3', textShadow: '0 0 30px rgba(255,215,130,0.7)', letterSpacing: '0.1em', marginTop: 8 }}>
              LUMBAR SUPPORT… 💭
            </div>
            <div style={{ fontFamily: 'var(--font-hand)', fontSize: 28, color: '#ffd98a' }}>adult dream achieved</div>
          </div>
        </div>
      )}

      <div style={{ position: 'absolute', left: '50%', top: 40, transform: 'translateX(-50%)' }}>
        <PopWords text="my heart starts doing PARKOUR" at={aParkour} local={local} size={46} color="#ff5c8a" glow="rgba(255,0,110,0.6)" />
      </div>
      {local > aWifi - 0.2 && (
        <div style={{ position: 'absolute', left: '50%', bottom: 210, transform: 'translateX(-50%)', fontFamily: 'var(--font-display)', fontSize: 40, color: '#9fe8ff', textShadow: '0 0 34px rgba(0,229,255,0.65)', animation: 'pulse-glow 1.8s ease-in-out infinite', whiteSpace: 'nowrap' }}>
          Wi‑Fi and a dream ✨
        </div>
      )}

      <div style={{ position: 'absolute', left: '50%', bottom: 66, transform: 'translateX(-50%)', width: 1340, background: 'rgba(1,8,3,0.7)', borderRadius: 16, padding: '14px 24px', border: '1px solid rgba(57,255,136,0.2)' }}>
        <SyncLine chunkIdx={chunkIdx} wordIdx={wordIdx} size={32} color="#cfe9dd" activeColor="#39ff88" />
      </div>

      {/* glitch bands */}
      {glitch > 0 &&
        [...Array(6)].map((_, i) => (
          <div
            key={i}
            style={{
              position: 'absolute', left: 0, width: '100%', height: 10 + hash(i) * 30,
              top: `${hash(i + 3) * 100}%`,
              background: i % 2 ? 'rgba(0,255,136,0.14)' : 'rgba(255,0,110,0.14)',
              transform: `translateX(${(hash(i + 7) - 0.5) * 160 * glitch}px)`,
              opacity: glitch,
            }}
          />
        ))}
      <div className="grain abs-fill" />
    </div>
  );
}

/** Scrolling EKG waveform canvas with beat spikes (or flatline). */
function Ekg({ local, flat }: { local: number; flat: boolean }) {
  const ref = useRef<HTMLCanvasElement>(null);
  const flatRef = useRef(flat);
  flatRef.current = flat;
  useEffect(() => {
    const cv = ref.current;
    if (!cv) return;
    const ctx = cv.getContext('2d');
    if (!ctx) return;
    let raf = 0;
    const W = 1600;
    const H = 900;
    let t = local * 1000;
    const beatWave = (x: number) => {
      const cycle = (x % 1.1) / 1.1;
      if (cycle < 0.08) return Math.sin(cycle / 0.08 * Math.PI) * 0.16;
      if (cycle < 0.12) return -(cycle - 0.08) / 0.04 * 0.28;
      if (cycle < 0.16) return -0.28 + (cycle - 0.12) / 0.04 * 1.28;
      if (cycle < 0.2) return 1 - (cycle - 0.16) / 0.04 * 1.55;
      if (cycle < 0.24) return -0.55 + (cycle - 0.2) / 0.04 * 0.55;
      if (cycle < 0.45) return Math.sin((cycle - 0.24) / 0.21 * Math.PI) * 0.18;
      return 0;
    };
    const frame = (now: number) => {
      t += 16;
      ctx.clearRect(0, 0, W, H);
      ctx.strokeStyle = 'rgba(57,255,136,0.08)';
      ctx.lineWidth = 1;
      for (let x = 0; x < W; x += 44) {
        ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x, H); ctx.stroke();
      }
      for (let y = 0; y < H; y += 44) {
        ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(W, y); ctx.stroke();
      }
      ctx.strokeStyle = flatRef.current ? 'rgba(57,255,136,0.75)' : '#39ff88';
      ctx.lineWidth = 3.4;
      ctx.shadowColor = '#39ff88';
      ctx.shadowBlur = 16;
      ctx.beginPath();
      const speed = 0.00022;
      for (let x = 0; x <= W; x += 4) {
        const ph = t * speed + x * 0.0016;
        const y = H / 2 - (flatRef.current ? Math.sin(ph) * 2 : beatWave(ph) * 300);
        if (x === 0) ctx.moveTo(x, y);
        else ctx.lineTo(x, y);
      }
      ctx.stroke();
      ctx.shadowBlur = 0;
      raf = requestAnimationFrame(frame);
    };
    raf = requestAnimationFrame(frame);
    return () => cancelAnimationFrame(raf);
  }, []); // eslint-disable-line react-hooks/exhaustive-deps
  return <canvas ref={ref} width={1600} height={900} className="abs-fill" style={{ width: '100%', height: '100%' }} aria-hidden />;
}

/** Heart emoji hopping between platforms, deterministic in local time. */
function HeartParkour({ local, start, glitch }: { local: number; start: number; glitch: number }) {
  if (!isFinite(start)) return null;
  const t = Math.max(0, local - start);
  const hopPeriod = 0.62;
  const hopN = Math.floor(t / hopPeriod);
  const hopP = (t % hopPeriod) / hopPeriod;
  const xs = [0, 1, 2, 3, 1, 2, 0, 3, 2, 1, 3, 0];
  const xi = xs[hopN % xs.length];
  const xj = xs[(hopN + 1) % xs.length];
  const xLerp = xi + (xj - xi) * hopP;
  const x = 250 + xLerp * 320;
  const arc = Math.sin(hopP * Math.PI);
  const y = 620 - arc * 130 + Math.sin(t * 2.4) * 8;
  const platforms = [0, 1, 2, 3].map((i) => ({
    left: 210 + i * 320,
    top: 660 + Math.sin(i * 2.1) * 36,
    label: ['📊', '💳', '📦', '💭'][i],
  }));
  return (
    <div style={{ position: 'absolute', inset: 0, opacity: 1 - glitch }}>
      {platforms.map((p, i) => (
        <div key={i} style={{ position: 'absolute', left: p.left, top: p.top, fontSize: 54, filter: 'drop-shadow(0 8px 20px rgba(0,0,0,0.5))', animation: `floaty-soft ${2.4 + i * 0.3}s ease-in-out infinite` }}>
          {p.label}
          <div style={{ width: 130, height: 10, borderRadius: 6, background: 'rgba(57,255,136,0.4)', margin: '6px auto 0' }} />
        </div>
      ))}
      <div
        style={{
          position: 'absolute', left: x, top: y, fontSize: 92,
          transform: `translateX(-50%) rotate(${hopP * 360}deg) scale(${1 + arc * 0.18})`,
          filter: 'drop-shadow(0 0 34px rgba(255,0,110,0.75))',
        }}
      >
        🫀
      </div>
      {/* stress lines */}
      {[...Array(8)].map((_, i) => {
        const ang = (i / 8) * Math.PI * 2 + t * 0.7;
        return (
          <span key={i} style={{ position: 'absolute', left: x + Math.cos(ang) * 90, top: y + Math.sin(ang) * 70, fontSize: 20, color: '#ff5c8a', opacity: 0.4 + 0.4 * Math.sin(t * 6 + i) }}>
            〰️
          </span>
        );
      })}
    </div>
  );
}
