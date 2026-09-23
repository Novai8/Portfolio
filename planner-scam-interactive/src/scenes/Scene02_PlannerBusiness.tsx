import { SceneProps, SyncLine, PopWords, Sticker, Reveal, anchorLocal } from './kit';
import { beat } from '../lib/animationHelpers';

/**
 * SCENE 02 — "The Planner Business"  (clean peach→mint product UI)
 * Rotating 3D planner carousel, passive-aggressive sticker, letter-by-letter
 * copy, floating shapes. Scrappy startup energy.
 */
const CARDS = [
  { grad: 'linear-gradient(150deg,#ff9a76,#ff5c8a)', label: 'Weekly Reset', emoji: '🗓️' },
  { grad: 'linear-gradient(150deg,#63e6be,#38b2ac)', label: 'Invoice Tracker', emoji: '📈' },
  { grad: 'linear-gradient(150deg,#ffd35c,#ff9a3c)', label: 'Deep Work', emoji: '🎯' },
];

export function Scene02({ active, local, chunkIdx, wordIdx }: SceneProps & { chunkIdx: number }) {
  if (!active) return <div className="scene-inner" />;
  const aLaunched = anchorLocal(2, 'launched');
  const aPlanners = anchorLocal(2, 'planners');
  const aSticker = anchorLocal(2, 'sticker');
  const end = 17.4;
  const out = Math.max(0, (local - (end - 0.7)) / 0.7); // cards scatter

  const spin = local * 26;

  return (
    <div className="scene-inner" style={{ transform: `translate(${out * (Math.random() < 0 ? 0 : 0)}px,0)` }}>
      {/* light background handled by MotionBackground palette; add product-clean shapes */}
      <div className="layer" style={{ left: '8%', top: '12%', width: 220, height: 220, borderRadius: '50%', background: 'rgba(255,255,255,0.25)', animation: 'floaty 7s ease-in-out infinite' }} />
      <div className="layer" style={{ right: '10%', top: '20%', width: 0, height: 0, borderLeft: '70px solid transparent', borderRight: '70px solid transparent', borderBottom: '120px solid rgba(255,255,255,0.2)', animation: 'spin-slow 22s linear infinite' }} />
      <div className="layer" style={{ left: '16%', bottom: '18%', width: 160, height: 160, borderRadius: 40, background: 'rgba(14,159,110,0.14)', transform: 'rotate(18deg)', animation: 'floaty-soft 6s ease-in-out infinite' }} />

      {/* headline */}
      <div style={{ position: 'absolute', left: '50%', top: 70, transform: 'translateX(-50%)', color: '#123', width: 1300, textAlign: 'center' }}>
        <PopWords text="a tiny online shop" at={aLaunched + 1.1} local={local} size={54} color="#16324a" />
        <div style={{ marginTop: 10, minHeight: 66, fontFamily: 'var(--font-mono)', fontWeight: 700, fontSize: 34, color: '#0e9f6e' }}>
          <Typewriter text="custom productivity planners" at={aPlanners} dur={1.1} local={local} />
        </div>
      </div>

      {/* 3D rotating planner carousel */}
      <div
        style={{
          position: 'absolute', left: '50%', top: 380,
          transform: `translateX(-50%) perspective(1200px) rotateX(12deg) scale(${1 - out * 0.4})`,
          transformStyle: 'preserve-3d',
          opacity: 1 - out,
        }}
      >
        <div style={{ position: 'relative', width: 900, height: 330, transformStyle: 'preserve-3d', transform: `rotateY(${spin}deg)` }}>
          {CARDS.map((c, i) => (
            <div
              key={i}
              style={{
                position: 'absolute', left: 300, top: 10, width: 300, height: 310,
                margin: '0 0 0 -150px',
                borderRadius: 22,
                background: c.grad,
                transform: `rotateY(${i * 120}deg) translateZ(340px)`,
                boxShadow: '0 34px 70px rgba(20,40,60,0.35)',
                display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center',
                gap: 14, color: '#fff',
              }}
            >
              <div style={{ fontSize: 74 }}>{c.emoji}</div>
              <div style={{ fontFamily: 'var(--font-display)', fontSize: 26, letterSpacing: '0.04em' }}>{c.label}</div>
              <div style={{ width: 180, height: 8, borderRadius: 6, background: 'rgba(255,255,255,0.55)' }} />
              <div style={{ width: 130, height: 8, borderRadius: 6, background: 'rgba(255,255,255,0.4)' }} />
              <div style={{ fontFamily: 'var(--font-hand)', fontSize: 26, color: 'rgba(255,255,255,0.95)' }}>
                funny prompt inside ✏️
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* icon row */}
      <div style={{ position: 'absolute', left: '50%', bottom: 268, transform: 'translateX(-50%)', display: 'flex', gap: 40 }}>
        {['✏️ drawing checkmarks', '🗒️ sticky notes peel', '😈 passive-aggressive stickers'].map((t, i) => {
          const p = beat(local, aPlanners + 0.4 + i * 0.5, 0.45);
          return (
            <div key={i} style={{ opacity: p, transform: `translateY(${(1 - p) * 30}px) rotate(${(1 - p) * 8}deg)`, background: 'rgba(255,255,255,0.75)', borderRadius: 16, padding: '10px 20px', fontWeight: 700, color: '#16324a', fontSize: 19 }}>
              {t}
            </div>
          );
        })}
      </div>

      {/* THE sticker */}
      <div style={{ position: 'absolute', right: 120, top: 210, transform: `rotate(${8 + Math.sin(local * 2) * 3}deg)` }}>
        <Sticker at={aSticker} local={local} tilt={8} bg="#ffffff" color="#d92b3a" size={24} pad="18px 24px">
          “Did you actually send
          <br />
          that invoice?” 🙃
        </Sticker>
      </div>

      {/* narration (dark strip for legibility on light bg) */}
      <div
        style={{
          position: 'absolute', left: '50%', bottom: 90, transform: `translateX(-50%) scale(${1 - out * 0.5})`,
          width: 1360, background: 'rgba(10,16,30,0.72)', borderRadius: 18, padding: '16px 26px', backdropFilter: 'blur(10px)',
        }}
      >
        <SyncLine chunkIdx={chunkIdx} wordIdx={wordIdx} size={33} color="#eef2ff" activeColor="#38e2a2" />
      </div>
      <div className="grain abs-fill" style={{ opacity: 0.5 }} />
    </div>
  );
}

function Typewriter({ text, at, dur, local }: { text: string; at: number; dur: number; local: number }) {
  const p = beat(local, at, dur);
  const n = Math.floor(p * text.length);
  return (
    <span>
      {text.slice(0, n)}
      <span style={{ opacity: p >= 1 && Math.floor(local * 2) % 2 === 0 ? 0 : 1 }}>▌</span>
    </span>
  );
}
