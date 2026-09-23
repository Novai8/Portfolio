import { SceneProps, SyncLine, PopWords, Reveal, Counter, CheckRow, anchorLocal } from './kit';
import { beat, clamp, hash } from '../lib/animationHelpers';

/**
 * SCENE 16 — "Security Lockdown"  (blue tech-grid control panel)
 * Screenshot flash, cancelled dashboard, traffic-spike graph, bootcamp badge,
 * six security toggles ticking on, traffic turning green, peaceful ripple.
 */
const CHECKS: Array<{ key: string; label: string }> = [
  { key: 'filters', label: 'stricter fraud filters' },
  { key: 'regions', label: 'block certain regions' },
  { key: 'verify', label: 'address verification' },
  { key: 'bulk', label: 'disable bulk quantities' },
  { key: 'captcha', label: 'captcha on checkout' },
  { key: 'breathe', label: 'breathe 🧘' },
];

export function Scene16({ active, local, chunkIdx, wordIdx }: SceneProps & { chunkIdx: number }) {
  if (!active) return <div className="scene-inner" />;
  const aScreenshot = anchorLocal(16, 'screenshot');
  const aCancelled = anchorLocal(16, 'cancelled');
  const aSpikes = anchorLocal(16, 'spikes');
  const aVending = anchorLocal(16, 'vending');
  const aBootcamp = anchorLocal(16, 'bootcamp');
  const aDrops = anchorLocal(16, 'drops');
  const aSilence = anchorLocal(16, 'silence');
  const end = 79.7;
  const white = clamp((local - (end - 1.2)) / 1.2);
  const green = beat(local, aDrops, 0.8);

  return (
    <div className="scene-inner">
      {/* tech grid */}
      <div
        className="abs-fill"
        style={{
          backgroundImage:
            'linear-gradient(rgba(0,194,255,0.10) 1px, transparent 1px), linear-gradient(90deg, rgba(0,194,255,0.10) 1px, transparent 1px)',
          backgroundSize: '70px 70px',
          animation: 'grid-pan 2.8s linear infinite',
        }}
      />
      <div className="abs-fill" style={{ background: 'radial-gradient(70% 70% at 50% 30%, rgba(0,194,255,0.10), transparent 70%)' }} />

      {/* screenshot flash */}
      {local > aScreenshot - 0.3 && local < aScreenshot + 1.4 && (
        <div className="abs-fill" style={{ background: '#fff', opacity: (1 - beat(local, aScreenshot - 0.3, 0.3)) * 0.9 }} />
      )}

      {/* cancelled dashboard */}
      <Reveal at={aCancelled - 0.6} local={local} rise={26} style={{ position: 'absolute', left: '50%', top: 100, transform: 'translateX(-50%)' }}>
        <div className="card" style={{ padding: '20px 44px', borderColor: 'rgba(0,255,136,0.5)', background: 'rgba(3,18,12,0.75)', textAlign: 'center' }}>
          <div style={{ fontFamily: 'var(--font-mono)', fontSize: 13, letterSpacing: '0.3em', color: '#7dd8a8' }}>ORDER #1043</div>
          <div style={{ fontFamily: 'var(--font-display)', fontSize: 44, color: '#00ff88', textShadow: '0 0 34px rgba(0,255,136,0.5)', marginTop: 4 }}>
            CANCELLED ✓ · FUNDS REVERSED · NO SHIPMENT
          </div>
        </div>
      </Reveal>

      {/* traffic graph */}
      <Reveal at={aSpikes - 0.5} local={local} rise={30} style={{ position: 'absolute', left: 120, top: 300 }}>
        <div className="card" style={{ width: 560, padding: '22px 28px', background: 'rgba(2,8,16,0.8)' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span style={{ fontFamily: 'var(--font-mono)', fontSize: 13, letterSpacing: '0.22em', color: '#9fc6ff' }}>CHECKOUT TRAFFIC · LIVE</span>
            <span style={{ fontFamily: 'var(--font-mono)', fontSize: 22, color: green > 0.5 ? '#00ff88' : '#ff4646', fontWeight: 700 }}>
              <Counter target={847} at={aSpikes + 0.2} dur={2} local={local} suffix=" hits" />
            </span>
          </div>
          <div style={{ display: 'flex', alignItems: 'flex-end', gap: 7, height: 150, marginTop: 16 }}>
            {[...Array(26)].map((_, i) => {
              const t = i / 26;
              const spike = t < 0.55 ? 0.25 + hash(i) * 0.55 + t * 0.9 : Math.max(0.06, (1 - (t - 0.55) / 0.45)) * (0.3 + hash(i) * 0.4);
              const h = 10 + spike * 130 * (green > 0 ? 1 - green * 0.85 : 1);
              const col = green > 0.5 ? '#00ff88' : '#ff4646';
              return <div key={i} style={{ flex: 1, height: h, background: `linear-gradient(180deg, ${col}, ${col}55)`, borderRadius: 4, opacity: beat(local, aSpikes + 0.2 + i * 0.05, 0.3), boxShadow: `0 0 12px ${col}44` }} />;
            })}
          </div>
          <div style={{ marginTop: 10, fontFamily: 'var(--font-mono)', fontSize: 12.5, color: green > 0.5 ? '#7dd8a8' : '#ff8fa3', letterSpacing: '0.14em' }}>
            {green > 0.5 ? '↓ traffic dropping… silence returns' : '⚠ bot barrage · testing cards · different names'}
          </div>
        </div>
      </Reveal>

      {/* vending machine line */}
      {local > aVending - 0.3 && (
        <div style={{ position: 'absolute', right: 140, top: 300, width: 430, opacity: beat(local, aVending - 0.3, 0.4), transform: 'rotate(2deg)' }}>
          <div className="card" style={{ padding: '20px 26px', background: 'rgba(20,4,10,0.75)', borderColor: 'rgba(255,70,70,0.4)' }}>
            <div style={{ fontSize: 46 }}>🥤</div>
            <div style={{ fontFamily: 'var(--font-display)', fontSize: 28, color: '#ff8fa3', marginTop: 6, lineHeight: 1.25 }}>
              “Oh my god, I'm a vending machine to them.”
            </div>
          </div>
        </div>
      )}

      {/* bootcamp badge */}
      <div style={{ position: 'absolute', left: '50%', top: 210, transform: 'translateX(-50%)' }}>
        <PopWords text="⚡ the fastest entrepreneur bootcamp — 20 minutes" at={aBootcamp - 0.4} local={local} size={34} color="#9fe8ff" glow="rgba(0,194,255,0.5)" />
      </div>

      {/* security checklist */}
      <Reveal at={aBootcamp + 0.5} local={local} rise={26} style={{ position: 'absolute', right: 130, top: 470 }}>
        <div className="card" style={{ width: 470, padding: '22px 30px', background: 'rgba(2,10,18,0.85)', borderColor: 'rgba(0,194,255,0.35)' }}>
          <div style={{ fontFamily: 'var(--font-mono)', fontSize: 13, letterSpacing: '0.25em', color: '#9fc6ff', marginBottom: 14 }}>
            LOCKDOWN CHECKLIST
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 11 }}>
            {CHECKS.map((c) => {
              const at = anchorLocal(16, c.key);
              const on = beat(local, at - 0.15, 0.4);
              return (
                <div key={c.key} style={{ display: 'flex', alignItems: 'center', gap: 14, opacity: 0.35 + 0.65 * on }}>
                  {/* toggle */}
                  <div style={{ width: 52, height: 28, borderRadius: 16, background: on > 0.5 ? '#00c2ff' : 'rgba(255,255,255,0.14)', position: 'relative', transition: 'background 0.2s', boxShadow: on > 0.5 ? '0 0 18px rgba(0,194,255,0.55)' : undefined }}>
                    <div style={{ position: 'absolute', top: 3, left: on > 0.5 ? 27 : 3, width: 22, height: 22, borderRadius: '50%', background: '#fff', transition: 'left 0.2s cubic-bezier(.34,1.56,.64,1)' }} />
                  </div>
                  <span style={{ fontWeight: 700, color: on > 0.5 ? '#e6f7ff' : '#7f95b5', fontSize: 19.5 }}>{c.label}</span>
                  <span style={{ marginLeft: 'auto', opacity: on }}>{on > 0.5 ? '✅' : '⬜'}</span>
                </div>
              );
            })}
          </div>
        </div>
      </Reveal>

      {/* peaceful ripple */}
      {local > aSilence - 0.3 &&
        [0, 1, 2].map((i) => (
          <span
            key={i}
            style={{
              position: 'absolute', left: '50%', top: '58%', width: 300, height: 300, margin: '-150px 0 0 -150px',
              borderRadius: '50%', border: '2px solid rgba(0,255,136,0.4)',
              animation: `ring-wave ${2.6}s ease-out ${i * 0.8}s infinite`,
            }}
          />
        ))}

      <div style={{ position: 'absolute', left: '50%', bottom: 52, transform: 'translateX(-50%)', width: 1320, background: 'rgba(2,8,14,0.85)', borderRadius: 16, padding: '14px 24px', border: '1px solid rgba(0,194,255,0.3)', opacity: 1 - white }}>
        <SyncLine chunkIdx={chunkIdx} wordIdx={wordIdx} size={30} color="#d5f0ff" activeColor="#00c2ff" />
      </div>

      {/* peaceful white fade OUT */}
      <div className="abs-fill" style={{ background: 'radial-gradient(80% 80% at 50% 50%, #eaffff, #ffffff)', opacity: white }} />
      <div className="grain abs-fill" />
    </div>
  );
}
