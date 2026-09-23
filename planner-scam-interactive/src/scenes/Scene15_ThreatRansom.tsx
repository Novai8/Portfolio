import { SceneProps, SyncLine, PopWords, Reveal, anchorLocal } from './kit';
import { beat, clamp, hash } from '../lib/animationHelpers';

/**
 * SCENE 15 — "Threat Email"  (ransom-note aesthetic)
 * Cut-out letter threat, puzzle-piece realization, lightbulb, scam-scheme
 * flowchart, shield appears.
 */
const RANSOM_COLORS = ['#ff4646', '#ffd35c', '#7dd8a8', '#9fc6ff', '#ff8ac2', '#fff'];

export function Scene15({ active, local, chunkIdx, wordIdx }: SceneProps & { chunkIdx: number }) {
  if (!active) return <div className="scene-inner" />;
  const aAnother = anchorLocal(15, 'another');
  const aOneHour = anchorLocal(15, 'onehour');
  const aClicks = anchorLocal(15, 'clicks');
  const aPressure = anchorLocal(15, 'pressure');
  const aYouWill = anchorLocal(15, 'youwillship');
  const aLaughFear = anchorLocal(15, 'laughfear');

  return (
    <div className="scene-inner" style={{ animation: 'jitter 0.5s steps(3) infinite' }}>
      {/* threat notification */}
      {local > aAnother - 0.3 && (
        <div style={{ position: 'absolute', left: '50%', top: 46, transform: `translateX(-50%) scale(${0.6 + 0.4 * beat(local, aAnother - 0.3, 0.35)})` }}>
          <div style={{ background: '#ff4646', color: '#fff', fontWeight: 900, borderRadius: 12, padding: '10px 24px', fontSize: 20, letterSpacing: '0.1em', boxShadow: '0 0 50px rgba(255,70,70,0.55)', animation: 'pulse-glow 0.9s infinite' }}>
            📩 NEW EMAIL · 2:41 AM
          </div>
        </div>
      )}

      {/* 1-hour threat email */}
      <Reveal at={aOneHour - 0.3} local={local} rise={26} style={{ position: 'absolute', left: '50%', top: 130, transform: 'translateX(-50%)' }}>
        <div className="card" style={{ width: 880, padding: '22px 34px', borderColor: 'rgba(255,70,70,0.6)', background: 'rgba(24,2,6,0.8)', transform: 'rotate(-1.2deg)' }}>
          <div style={{ fontFamily: 'var(--font-mono)', fontSize: 13, color: '#ff9db1', letterSpacing: '0.2em' }}>FROM: ELLIOT · SUBJECT: (no subject)</div>
          <div style={{ marginTop: 10, fontSize: 27, fontWeight: 900, color: '#ffdde3', fontFamily: 'var(--font-display)' }}>
            “IF YOU DON'T SHIP IN 1 HOUR I WILL REPORT YOU. <span style={{ color: '#ff4646' }}>REFUND ME NOW.”</span>
          </div>
        </div>
      </Reveal>

      {/* puzzle realization + lightbulb */}
      {local > aClicks - 1.4 && (
        <div style={{ position: 'absolute', right: 130, top: 300, display: 'grid', gridTemplateColumns: '64px 64px', gap: 6, transform: 'rotate(-6deg)' }}>
          {[...Array(4)].map((_, i) => {
            const p = beat(local, aClicks - 1.2 + i * 0.28, 0.35);
            return (
              <div
                key={i}
                style={{
                  width: 64, height: 64, background: ['#ffd35c', '#7dd8a8', '#9fc6ff', '#ff8ac2'][i],
                  borderRadius: 8, opacity: p, transform: `scale(${p}) rotate(${(1 - p) * 90}deg)`,
                  clipPath: 'polygon(10% 0, 90% 0, 100% 40%, 90% 60%, 100% 100%, 0 100%, 0 60%, 10% 40%)',
                  boxShadow: '0 8px 20px rgba(0,0,0,0.4)',
                }}
              />
            );
          })}
          <div style={{ gridColumn: 'span 2', textAlign: 'center', marginTop: 10, fontSize: 74, animation: 'pulse-glow 1.2s infinite', color: '#ffd35c', opacity: beat(local, aClicks - 1.3, 0.3) }}>
            💡
          </div>
        </div>
      )}

      {/* scheme flowchart */}
      {local > aPressure - 0.4 && (
        <Reveal at={aPressure - 0.4} local={local} rise={30} style={{ position: 'absolute', left: 130, top: 300 }}>
          <div className="card" style={{ width: 480, padding: '24px 30px', background: 'rgba(10,4,10,0.85)' }}>
            <div style={{ fontFamily: 'var(--font-mono)', fontSize: 13, letterSpacing: '0.25em', color: '#ff9db1', marginBottom: 14 }}>
              THE PRESSURE PLAYBOOK
            </div>
            {[
              ['😱 panic → hit “refund”', '#ff4646'],
              ['🕵️ money rerouted elsewhere', '#ff9a3c'],
              ['📦 shipment proof → dispute win', '#ffd35c'],
            ].map(([label, color], i) => {
              const p = beat(local, aPressure + i * 0.7, 0.45);
              return (
                <div key={i} style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 12, opacity: p, transform: `translateX(${(1 - p) * -26}px)` }}>
                  <span style={{ color, fontSize: 22, fontWeight: 900 }}>{'▼'}</span>
                  <span style={{ color: '#ffe8ec', fontWeight: 700, fontSize: 20 }}>{label}</span>
                </div>
              );
            })}
            <div style={{ fontFamily: 'var(--font-hand)', fontSize: 26, color: '#ffd6e0', marginTop: 6 }}>
              “this isn't about planners… it's about pressure.”
            </div>
          </div>
        </Reveal>
      )}

      {/* RANSOM NOTE */}
      {local > aYouWill - 0.5 && (
        <div style={{ position: 'absolute', left: '50%', top: 520, transform: 'translateX(-50%)', width: 1100, textAlign: 'center' }}>
          {['YOU WILL SHIP.', 'I KNOW WHERE YOU LIVE.'].map((line, li) => (
            <div key={li} style={{ marginBottom: 10 }}>
              {line.split('').map((ch, i) => {
                const p = beat(local, aYouWill - 0.4 + li * 0.5 + i * 0.032, 0.3);
                const h1 = hash(i + li * 31);
                return (
                  <span
                    key={i}
                    style={{
                      display: 'inline-block',
                      whiteSpace: 'pre',
                      fontFamily: h1 > 0.66 ? 'var(--font-display)' : h1 > 0.33 ? 'var(--font-mono)' : 'var(--font-hand)',
                      fontSize: 44 + h1 * 30,
                      color: RANSOM_COLORS[(i + li) % RANSOM_COLORS.length],
                      background: h1 > 0.5 ? 'rgba(255,255,255,0.9)' : 'transparent',
                      padding: h1 > 0.5 ? '0 4px' : 0,
                      transform: `rotate(${(h1 - 0.5) * 26}deg) translateY(${(1 - p) * -80}px) scale(${0.4 + 0.6 * p})`,
                      opacity: p,
                      margin: '0 2px',
                      boxShadow: h1 > 0.5 ? '0 6px 16px rgba(0,0,0,0.35)' : undefined,
                      textShadow: '0 4px 0 rgba(0,0,0,0.45)',
                    }}
                  >
                    {ch}
                  </span>
                );
              })}
            </div>
          ))}
        </div>
      )}

      {/* shield */}
      {local > aLaughFear + 0.6 && (
        <div
          style={{
            position: 'absolute', right: 170, bottom: 130, fontSize: 120,
            transform: `scale(${beat(local, aLaughFear + 0.6, 0.6)}) rotate(${-6 + Math.sin(local * 2) * 4}deg)`,
            filter: 'drop-shadow(0 0 50px rgba(125,216,168,0.8))',
          }}
        >
          🛡️
        </div>
      )}

      <div style={{ position: 'absolute', left: '50%', top: 470, transform: 'translateX(-50%)' }}>
        <PopWords text="I laugh… but it's fear wearing a comedy mask 🎭" at={aLaughFear - 0.5} local={local} size={30} color="#ffd6e0" />
      </div>

      <div style={{ position: 'absolute', left: '50%', bottom: 46, transform: 'translateX(-50%)', width: 1320, background: 'rgba(10,1,3,0.85)', borderRadius: 16, padding: '14px 24px', border: '1px solid rgba(255,70,70,0.35)' }}>
        <SyncLine chunkIdx={chunkIdx} wordIdx={wordIdx} size={30} color="#ffe0e6" activeColor="#ff4646" />
      </div>
      <div className="grain abs-fill" />
    </div>
  );
}
