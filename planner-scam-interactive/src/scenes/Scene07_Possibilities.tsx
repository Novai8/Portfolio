import { SceneProps, SyncLine, PopWords, Reveal, anchorLocal } from './kit';
import { beat, clamp, hash } from '../lib/animationHelpers';

/**
 * SCENE 07 — "Three Possibilities"  (minimal infographic, light paper)
 * Venn-style circles: billionaire / scammed / raccoon-billionaire, paw-print
 * trail, merge-to-envelope transition.
 */
const CIRCLES = [
  { icon: '💰', label: 'MYSTERIOUS BILLIONAIRE', sub: 'loves planners?', color: '#ffd35c', dark: '#7a5a00' },
  { icon: '🕳️', label: 'SPECTACULARLY SCAMMED', sub: 'trap door', color: '#ff4646', dark: '#7a0f18' },
  { icon: '🦝', label: 'RACCOON BILLIONAIRE', sub: 'top hat & monocle', color: '#8f7bff', dark: '#372a7a' },
];

export function Scene07({ active, local, chunkIdx, wordIdx }: SceneProps & { chunkIdx: number }) {
  if (!active) return <div className="scene-inner" />;
  const aPoss = anchorLocal(7, 'possibilities');
  const aOne = anchorLocal(7, 'one');
  const aScammed = anchorLocal(7, 'scammed');
  const aThree = anchorLocal(7, 'three');
  const end = 19.8;
  const merge = clamp((local - (end - 0.9)) / 0.9);

  const times = [aPoss + 0.2, aOne + 0.1, aScammed + 0.9];

  return (
    <div className="scene-inner" style={{ transform: `scale(${1 - merge * 0.35})`, filter: `blur(${merge * 6}px)` }}>
      {/* thought connectors */}
      <svg className="abs-fill" width="1600" height="900">
        {CIRCLES.map((c, i) => {
          const p = beat(local, times[i] - 0.3, 0.5);
          const cx = 380 + i * 420;
          return (
            <path
              key={i}
              d={`M 800 250 C ${700 - i * 40} ${330}, ${cx} ${240}, ${cx} ${430}`}
              stroke={c.color}
              strokeWidth={3}
              fill="none"
              strokeDasharray="10 8"
              opacity={p * 0.65}
              strokeDashoffset={0}
              style={{ animation: 'dashmove 1.2s linear infinite' }}
            />
          );
        })}
      </svg>

      <div style={{ position: 'absolute', left: '50%', top: 64, transform: 'translateX(-50%)' }}>
        <PopWords text="only TWO possibilities → fine, THREE" at={aPoss} local={local} size={44} color="#23262e" />
      </div>

      {/* three panels */}
      <div style={{ position: 'absolute', left: '50%', top: 330, transform: 'translateX(-50%)', display: 'flex', gap: 44 }}>
        {CIRCLES.map((c, i) => {
          const p = beat(local, times[i], 0.55);
          const shakeIt = i === 1 && local > aScammed && local < aScammed + 0.8;
          return (
            <div
              key={i}
              className={shakeIt ? 'shake-hard' : undefined}
              style={{
                width: 380, borderRadius: 28, padding: '34px 28px 30px', textAlign: 'center',
                background: `linear-gradient(165deg, #ffffff, ${c.color}22)`,
                border: `3px solid ${c.color}`,
                boxShadow: `0 30px 70px rgba(30,30,60,0.16), 0 0 0 ${Math.round(p * 14) - 14}px ${c.color}22`,
                transform: `translateY(${(1 - p) * 80}px) rotate(${(hash(i) - 0.5) * 6 * p}deg) scale(${0.7 + 0.3 * p})`,
                opacity: p,
              }}
            >
              <div style={{ width: 150, height: 150, margin: '0 auto', borderRadius: '50%', background: `${c.color}33`, display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 76, animation: 'floaty-soft 2.8s ease-in-out infinite', boxShadow: `0 0 44px ${c.color}55` }}>
                {c.icon}
                {i === 2 && <span style={{ fontSize: 44, position: 'absolute', marginTop: -60, marginLeft: 60 }}>🎩</span>}
              </div>
              <div style={{ fontFamily: 'var(--font-display)', fontSize: 25, color: c.dark, marginTop: 20, letterSpacing: '0.02em' }}>
                {i + 1}. {c.label}
              </div>
              <div style={{ fontFamily: 'var(--font-hand)', fontSize: 26, color: '#666', marginTop: 6 }}>{c.sub}</div>
              {i === 2 && (
                <div style={{ marginTop: 10, fontSize: 22, letterSpacing: 14, opacity: 0.8 }}>
                  {'🐾🐾🐾'.split('').map((p2, k) => (
                    <span key={k} style={{ display: 'inline-block', opacity: beat(local, aScammed + 1.1 + k * 0.18, 0.3), transform: `rotate(${k * 14}deg)` }}>{p2}</span>
                  ))}
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* merge envelope */}
      {merge > 0 && (
        <div style={{ position: 'absolute', left: '50%', top: '42%', transform: `translate(-50%,-50%) scale(${merge * 2.4})`, fontSize: 120, opacity: merge, filter: `drop-shadow(0 0 40px rgba(143,123,255,0.8))` }}>
          ✉️
        </div>
      )}

      <div style={{ position: 'absolute', left: '50%', bottom: 70, transform: 'translateX(-50%)', width: 1280, background: 'rgba(22,24,34,0.85)', borderRadius: 16, padding: '14px 24px' }}>
        <SyncLine chunkIdx={chunkIdx} wordIdx={wordIdx} size={32} color="#eef0f6" activeColor="#8f7bff" />
      </div>
    </div>
  );
}
