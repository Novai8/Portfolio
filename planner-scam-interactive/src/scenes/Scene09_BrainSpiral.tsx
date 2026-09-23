import { SceneProps, SyncLine, PopWords, Reveal, anchorLocal } from './kit';
import { beat, clamp, hash } from '../lib/animationHelpers';

/**
 * SCENE 09 — "Brain Spiral"  (conspiracy cork board)
 * Horror-story polaroids pinned by red string, newspaper clippings, stress
 * meter, string snap + board collapse.
 */
const POLAROIDS = [
  { icon: '💳', label: 'CHARGEBACK', sub: 'card + X', color: '#ff5c5c', rot: -7 },
  { icon: '⚡', label: 'FAKE CARD', sub: 'glitching', color: '#ffd35c', rot: 4 },
  { icon: '⚖️', label: 'DISPUTE', sub: '“delivered” (it was not)', color: '#8fd3ff', rot: -3 },
];

export function Scene09({ active, local, chunkIdx, wordIdx }: SceneProps & { chunkIdx: number }) {
  if (!active) return <div className="scene-inner" />;
  const aBrain = anchorLocal(9, 'brain');
  const aCharge = anchorLocal(9, 'chargebacks');
  const aDelivered = anchorLocal(9, 'delivered');
  const aNever = anchorLocal(9, 'never');
  const end = 11.9;
  const snap = clamp((local - (end - 1.1)) / 1.1);

  const boardFall = snap * snap;

  return (
    <div className="scene-inner" style={{ perspective: '1200px' }}>
      {/* cork board */}
      <div
        className="abs-fill"
        style={{
          background: 'radial-gradient(120% 120% at 50% 0%, #a06a3c 0%, #6d4423 55%, #4a2c14 100%)',
          transform: `rotateX(${boardFall * 70}deg) translateY(${boardFall * 420}px)`,
          transformOrigin: 'top center',
        }}
      >
        {/* cork speckles */}
        {[...Array(60)].map((_, i) => (
          <span key={i} style={{ position: 'absolute', left: `${hash(i) * 100}%`, top: `${hash(i + 30) * 100}%`, width: 3 + hash(i + 3) * 4, height: 3 + hash(i + 6) * 4, borderRadius: '50%', background: `rgba(60,34,12,${0.2 + hash(i + 9) * 0.3})` }} />
        ))}
        <div className="abs-fill" style={{ boxShadow: 'inset 0 0 220px rgba(20,8,0,0.75)' }} />

        <div style={{ position: 'absolute', left: '50%', top: 48, transform: 'translateX(-50%)' }}>
          <PopWords text="every horror story I've ever read:" at={aBrain + 0.6} local={local} size={42} color="#ffe9c9" />
        </div>

        {/* red string */}
        <svg className="abs-fill" width="1600" height="900" style={{ opacity: 1 - boardFall }}>
          <path
            d="M 360 420 C 560 260, 760 560, 800 400 C 850 220, 1080 540, 1240 380"
            stroke="#ff2b2b"
            strokeWidth={3.4}
            fill="none"
            strokeDasharray="1800"
            strokeDashoffset={1800 * (1 - clamp((local - aCharge + 0.4) / 2.4))}
            style={{ filter: 'drop-shadow(0 0 8px rgba(255,43,43,0.7))' }}
          />
          {[360, 800, 1240].map((x, i) => (
            <circle key={i} cx={x} cy={[420, 400, 380][i]} r={9} fill="#ff2b2b" opacity={clamp((local - aCharge + 0.4 - i) * 2)} />
          ))}
        </svg>

        {/* polaroids */}
        {POLAROIDS.map((p, i) => {
          const at = aCharge - 0.3 + i * 0.85;
          const pin = beat(local, at, 0.45);
          return (
            <div
              key={i}
              style={{
                position: 'absolute', left: 240 + i * 430, top: 300 + (i % 2) * 90,
                transform: `rotate(${p.rot + Math.sin(local * 1.4 + i) * 2}deg) scale(${0.5 + 0.5 * pin}) translateY(${(1 - pin) * -60}px)`,
                opacity: pin,
                width: 300,
              }}
            >
              <div style={{ position: 'absolute', left: '50%', top: -14, transform: 'translateX(-50%)', width: 18, height: 18, borderRadius: '50%', background: '#ff2b2b', boxShadow: '0 4px 10px rgba(0,0,0,0.5)' }} />
              <div style={{ background: '#fdf8ee', borderRadius: 8, padding: '16px 16px 20px', boxShadow: '0 26px 50px rgba(30,10,0,0.5)', textAlign: 'center' }}>
                <div style={{ fontSize: 84, filter: i === 1 ? `hue-rotate(${Math.sin(local * 20) * 60}deg)` : undefined }}>{p.icon}</div>
                <div style={{ fontFamily: 'var(--font-display)', fontSize: 20, color: '#31210f', marginTop: 8 }}>{p.label}</div>
                <div style={{ fontFamily: 'var(--font-hand)', fontSize: 24, color: '#6b5232' }}>{p.sub}</div>
              </div>
            </div>
          );
        })}

        {/* newspaper clippings */}
        {local > aDelivered - 0.5 &&
          ['FAKE CARDS ON THE RISE', '“DELIVERED” DISPUTES DOUBLE', 'SELLER BEWARE'].map((h, i) => {
            const p = beat(local, aDelivered - 0.4 + i * 0.5, 0.5);
            return (
              <div
                key={i}
                style={{
                  position: 'absolute', right: 120 + i * 30, top: 560 + i * 54,
                  transform: `rotate(${(hash(i) - 0.5) * 10}deg) translateY(${(1 - p) * 40}px)`,
                  opacity: p * 0.95,
                  background: '#f1ead8', color: '#2a2118', padding: '10px 18px',
                  fontFamily: 'var(--font-display)', fontSize: 17, letterSpacing: '0.06em',
                  boxShadow: '0 16px 30px rgba(30,10,0,0.45)',
                  animation: `floaty-soft ${2.6 + i * 0.4}s ease-in-out infinite`,
                }}
              >
                📰 {h}
              </div>
            );
          })}

        {/* fake review card */}
        {local > aNever && (
          <div style={{ position: 'absolute', left: '50%', bottom: 200, transform: 'translateX(-50%) rotate(-1.4deg)', opacity: beat(local, aNever, 0.4) }}>
            <div style={{ background: 'rgba(10,10,14,0.85)', border: '2px solid #ff5c5c', borderRadius: 14, padding: '14px 26px', color: '#ffd9d9', fontFamily: 'var(--font-mono)', fontSize: 21, boxShadow: '0 0 44px rgba(255,92,92,0.35)' }}>
              ⭐ 1/5 — “I nEvEr ReCeIvEd iT” 🎭
            </div>
          </div>
        )}
      </div>

      {/* stress meter */}
      <Reveal at={aNever - 0.9} local={local} rise={20} style={{ position: 'absolute', left: 120, bottom: 120 }}>
        <div style={{ background: 'rgba(8,6,4,0.7)', border: '1px solid rgba(255,92,92,0.4)', borderRadius: 14, padding: '16px 22px' }}>
          <div style={{ fontFamily: 'var(--font-mono)', fontSize: 12.5, letterSpacing: '0.25em', color: '#ff9d9d', marginBottom: 10 }}>STRESS METER</div>
          <div style={{ width: 300, height: 16, borderRadius: 10, background: 'rgba(255,255,255,0.1)', overflow: 'hidden' }}>
            <div style={{ width: `${clamp((local - aNever + 0.9) / 1.6) * 100}%`, height: '100%', background: 'linear-gradient(90deg,#ffd35c,#ff4646)', boxShadow: '0 0 18px rgba(255,70,70,0.7)' }} />
          </div>
        </div>
      </Reveal>

      <div style={{ position: 'absolute', left: '50%', bottom: 40, transform: `translateX(-50%) translateY(${boardFall * -30}px)`, width: 1300, background: 'rgba(12,8,4,0.8)', borderRadius: 16, padding: '14px 24px', opacity: 1 - boardFall }}>
        <SyncLine chunkIdx={chunkIdx} wordIdx={wordIdx} size={30} color="#f3e6d2" activeColor="#ffd35c" />
      </div>
      <div className="grain abs-fill" />
    </div>
  );
}
