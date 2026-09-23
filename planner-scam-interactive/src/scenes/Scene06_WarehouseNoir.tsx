import { SceneProps, SyncLine, PopWords, TypingText, Reveal, anchorLocal } from './kit';
import { beat, clamp, hash } from '../lib/animationHelpers';

/**
 * SCENE 06 — "Warehouse Discovery"  (Google-Maps noir)
 * Zooming map, bouncing pin, noir warehouse with spotlight, waving red flags,
 * magnifier radar, raccoon Easter egg, horror-drip "abandoned".
 */
export function Scene06({ active, local, chunkIdx, wordIdx }: SceneProps & { chunkIdx: number }) {
  if (!active) return <div className="scene-inner" />;
  const aAddress = anchorLocal(6, 'address');
  const aIndustrial = anchorLocal(6, 'industrial');
  const aSuite = anchorLocal(6, 'suite');
  const aMap = anchorLocal(6, 'map');
  const aWarehouse = anchorLocal(6, 'warehouse');
  const aRaccoon = anchorLocal(6, 'raccoon');
  const aDrain = anchorLocal(6, 'drain');
  const end = 29.2;
  const crumple = clamp((local - (end - 0.8)) / 0.8);

  return (
    <div className="scene-inner" style={{ filter: `saturate(${1 - crumple * 0.8}) brightness(${1 - crumple * 0.4})`, transform: `scale(${1 - crumple * 0.12}) rotate(${crumple * -3}deg)` }}>
      {/* zooming map */}
      <div className="abs-fill" style={{ animation: 'zoom-bg 26s ease-in-out infinite alternate' }}>
        <div className="abs-fill" style={{ background: 'linear-gradient(160deg,#0d1017,#090a10)' }} />
        {/* streets */}
        <svg width="1600" height="900" style={{ position: 'absolute', inset: 0, opacity: 0.85 }}>
          {[
            'M -50 220 C 300 190, 700 260, 1650 200', 'M -50 460 C 400 500, 900 420, 1650 480',
            'M -50 700 C 500 660, 1100 740, 1650 690', 'M 240 -50 C 200 300, 300 600, 240 950',
            'M 620 -50 C 660 300, 580 620, 640 950', 'M 1050 -50 C 1000 300, 1120 600, 1060 950',
            'M 1380 -50 C 1420 300, 1330 620, 1400 950',
          ].map((d, i) => (
            <path key={i} d={d} stroke={i % 2 ? 'rgba(255,207,92,0.16)' : 'rgba(160,180,220,0.14)'} strokeWidth={i % 2 ? 12 : 8} fill="none" />
          ))}
          <rect x="1050" y="380" width="200" height="140" fill="rgba(255,70,70,0.12)" stroke="rgba(255,70,70,0.4)" strokeDasharray="8 6" />
        </svg>
        {/* blocks */}
        {[...Array(14)].map((_, i) => (
          <div key={i} style={{
            position: 'absolute', left: `${(hash(i) * 88 + 2)}%`, top: `${(hash(i + 20) * 82 + 4)}%`,
            width: 40 + hash(i + 5) * 90, height: 30 + hash(i + 9) * 60,
            background: 'rgba(120,140,180,0.06)', border: '1px solid rgba(160,180,220,0.08)', borderRadius: 4,
          }} />
        ))}
      </div>

      {/* warehouse silhouette */}
      <Reveal at={aWarehouse - 0.6} local={local} rise={20} style={{ position: 'absolute', left: '50%', top: 240, transform: 'translateX(-50%)' }}>
        <svg width="560" height="290" viewBox="0 0 560 290" style={{ filter: 'drop-shadow(0 30px 60px rgba(0,0,0,0.7))' }}>
          <defs>
            <linearGradient id="wh" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0" stopColor="#1a2030" />
              <stop offset="1" stopColor="#0a0d15" />
            </linearGradient>
          </defs>
          <path d="M30 270 L30 130 L280 40 L530 130 L530 270 Z" fill="url(#wh)" stroke="rgba(255,207,92,0.35)" strokeWidth="3" />
          <rect x="240" y="180" width="80" height="90" fill="#05070c" stroke="rgba(255,207,92,0.25)" />
          <rect x="80" y="170" width="90" height="60" fill="rgba(255,207,92,0.06)" stroke="rgba(255,207,92,0.2)" />
          <rect x="390" y="170" width="90" height="60" fill="rgba(255,207,92,0.06)" stroke="rgba(255,207,92,0.2)" />
          {/* spotlight sweep */}
          <polygon points="280,40 180,290 380,290" fill="rgba(255,230,160,0.07)" style={{ transformOrigin: '280px 40px', animation: 'sway 5s ease-in-out infinite' }} />
        </svg>
      </Reveal>

      {/* falling pin */}
      {local > aIndustrial - 0.4 && (() => {
        const p = beat(local, aIndustrial - 0.4, 0.55);
        const bounce = p < 1 ? Math.abs(Math.sin(p * Math.PI * 2.5)) * (1 - p) : Math.abs(Math.sin(local * 2.4)) * 6;
        return (
          <div style={{ position: 'absolute', left: 1010, top: 300, fontSize: 76, transform: `translateY(${-140 * (1 - p) - bounce}px)`, filter: 'drop-shadow(0 10px 24px rgba(255,70,70,0.6))', opacity: clamp(p * 2) }}>
            📍
          </div>
        );
      })()}

      {/* red flags waving */}
      {local > aRaccoon - 1.2 &&
        [0, 1, 2].map((i) => (
          <div key={i} style={{ position: 'absolute', left: 1180 + i * 46, top: 330 - i * 14, fontSize: 42 + i * 6, animation: `flag-wave ${0.8 + i * 0.2}s ease-in-out infinite`, transformOrigin: 'bottom left' }}>
            🚩
          </div>
        ))}

      {/* magnifier radar */}
      <Reveal at={aMap - 0.3} local={local} rise={24} style={{ position: 'absolute', right: 130, top: 120 }}>
        <div style={{ position: 'relative', width: 200, height: 200, borderRadius: '50%', border: '4px solid rgba(255,207,92,0.6)', overflow: 'hidden', background: 'rgba(255,207,92,0.04)', boxShadow: '0 0 60px rgba(255,207,92,0.25)' }}>
          <div style={{ position: 'absolute', inset: 0, background: 'conic-gradient(from 0deg, rgba(255,207,92,0.5), transparent 24%)', animation: 'radar 2.6s linear infinite' }} />
          <div style={{ position: 'absolute', left: '48%', top: '48%', width: 14, height: 14, borderRadius: '50%', background: '#ff4646', boxShadow: '0 0 18px #ff4646', animation: 'ekg-flash 1s infinite' }} />
        </div>
        <div style={{ textAlign: 'center', fontSize: 60, marginTop: 6, animation: 'wobble 2s ease-in-out infinite' }}>🔍</div>
      </Reveal>

      {/* address readout */}
      <Reveal at={aSuite - 1.2} local={local} rise={20} style={{ position: 'absolute', left: 110, top: 150 }}>
        <div className="card" style={{ width: 470, padding: '20px 26px', background: 'rgba(4,6,10,0.8)', borderColor: 'rgba(255,207,92,0.3)' }}>
          <div style={{ fontFamily: 'var(--font-mono)', fontSize: 13, letterSpacing: '0.25em', color: '#ffcf5c' }}>SHIPPING ADDRESS</div>
          <div style={{ marginTop: 10, fontFamily: 'var(--font-mono)', fontSize: 21, color: '#dfe6ff', lineHeight: 1.7 }}>
            <TypingText text="9 REBAR YARD, INDUSTRIAL EDGE" at={aIndustrial} dur={1.2} local={local} />
            <br />
            <span style={{ color: '#ff5c5c' }}>{local > aSuite ? 'NO SUITE NUMBER.' : ''} {local > aSuite + 0.7 ? 'NO BUSINESS NAME.' : ''}</span>
          </div>
        </div>
      </Reveal>

      {/* horror drip text */}
      {local > aWarehouse - 0.2 && (
        <div style={{ position: 'absolute', left: '50%', bottom: 240, transform: 'translateX(-50%)', fontFamily: 'var(--font-display)', fontSize: 88, color: '#9fe8b8' }}>
          {'abandoned…'.split('').map((ch, i) => (
            <span key={i} style={{ display: 'inline-block', position: 'relative', color: i % 2 ? '#9fe8b8' : '#5cd692', transform: `rotate(${(hash(i) - 0.5) * 8}deg) translateY(${Math.sin(local * 3 + i) * 3}px)`, textShadow: '0 0 34px rgba(92,214,146,0.5)' }}>
              {ch === ' ' ? '\u00A0' : ch}
              {i % 3 === 0 && (
                <span style={{ position: 'absolute', left: '38%', top: '78%', fontSize: 14, color: '#5cd692', animation: `drip ${1.4 + hash(i)}s ease-in infinite` }}>▪</span>
              )}
            </span>
          ))}
        </div>
      )}

      {/* raccoon easter egg */}
      {local > aRaccoon - 0.2 && (
        <div style={{ position: 'absolute', right: 60, bottom: 0, fontSize: 90, animation: 'peek 4.5s ease-in-out infinite', transformOrigin: 'bottom center' }}>
          🦝
        </div>
      )}

      <div style={{ position: 'absolute', left: '50%', top: 40, transform: 'translateX(-50%)' }}>
        <PopWords text="and then I see the shipping address" at={aAddress} local={local} size={40} color="#ffcf5c" glow="rgba(255,207,92,0.5)" />
      </div>

      <div style={{ position: 'absolute', left: '50%', bottom: 60, transform: 'translateX(-50%)', width: 1340, background: 'rgba(3,4,8,0.78)', borderRadius: 16, padding: '14px 24px', border: '1px solid rgba(255,207,92,0.18)' }}>
        <SyncLine chunkIdx={chunkIdx} wordIdx={wordIdx} size={31} color="#dfe6ff" activeColor="#ffcf5c" />
      </div>
      <div className="grain abs-fill" />
    </div>
  );
}
