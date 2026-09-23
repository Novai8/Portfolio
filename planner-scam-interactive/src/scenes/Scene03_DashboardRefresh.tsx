import { SceneProps, SyncLine, PopWords, Reveal, anchorLocal } from './kit';
import { beat, pingpong } from '../lib/animationHelpers';

/**
 * SCENE 03 — "Dashboard Refresh"  (neon holographic store dashboard)
 * Browser window, obsessive refresh clicking, order counter 1…maybe 2,
 * heart particles for mom. Screen flash OUT.
 */
export function Scene03({ active, local, chunkIdx, wordIdx }: SceneProps & { chunkIdx: number }) {
  if (!active) return <div className="scene-inner" />;
  const aRefresh = anchorLocal(3, 'refresh');
  const aMaybe = anchorLocal(3, 'maybe2');
  const aMom = anchorLocal(3, 'mom');
  const end = 8.3;
  const flash = Math.max(0, (local - (end - 0.5)) / 0.5);
  const clickCycle = pingpong(local, 0.9, 0.2);

  return (
    <div className="scene-inner">
      {/* moving neon grid */}
      <div
        className="abs-fill"
        style={{
          backgroundImage:
            'linear-gradient(rgba(0,229,255,0.09) 1px, transparent 1px), linear-gradient(90deg, rgba(0,229,255,0.09) 1px, transparent 1px)',
          backgroundSize: '80px 80px',
          animation: 'grid-pan 3.2s linear infinite',
          maskImage: 'radial-gradient(70% 70% at 50% 45%, #000 30%, transparent 100%)',
        }}
      />

      {/* browser window */}
      <Reveal at={0.2} local={local} rise={30} style={{ position: 'absolute', left: 220, right: 220, top: 130 }}>
        <div
          className="card"
          style={{
            overflow: 'hidden',
            transform: `scale(${1 + flash * 0.25})`,
            filter: `brightness(${1 + flash * 2.4})`,
            boxShadow: '0 40px 120px rgba(0,229,255,0.18)',
          }}
        >
          {/* title bar */}
          <div style={{ display: 'flex', alignItems: 'center', gap: 10, padding: '12px 18px', background: 'rgba(255,255,255,0.05)', borderBottom: '1px solid rgba(255,255,255,0.1)' }}>
            {['#ff5f57', '#febc2e', '#28c840'].map((c) => (
              <span key={c} style={{ width: 14, height: 14, borderRadius: '50%', background: c }} />
            ))}
            <div style={{ marginLeft: 14, flex: 1, fontFamily: 'var(--font-mono)', fontSize: 14.5, color: '#9fe8ff', background: 'rgba(0,0,0,0.35)', borderRadius: 8, padding: '6px 14px' }}>
              🔒 store-dashboard-dot-com/orders
            </div>
            <div style={{ width: 26, height: 26, border: '3px solid rgba(0,229,255,0.25)', borderTopColor: '#00e5ff', borderRadius: '50%', animation: 'spin-slow 0.9s linear infinite' }} />
          </div>

          <div style={{ padding: '34px 42px', position: 'relative', minHeight: 380 }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <div style={{ fontFamily: 'var(--font-display)', fontSize: 30, color: '#dfeaff' }}>ORDERS</div>
              <div
                style={{
                  position: 'relative',
                  padding: '12px 26px', borderRadius: 12, background: 'linear-gradient(135deg,#00e5ff33,#00e5ff11)',
                  border: '1px solid rgba(0,229,255,0.5)', color: '#aef1ff', fontWeight: 700, letterSpacing: '0.1em',
                  transform: `scale(${1 - clickCycle * 0.08})`,
                }}
              >
                ⟳ REFRESH
                {/* giant cursor */}
                <div style={{ position: 'absolute', right: -34, bottom: -30, fontSize: 40, transform: `rotate(-14deg) translate(${clickCycle * -6}px, ${clickCycle * -6}px)` }}>🖱️</div>
              </div>
            </div>

            {/* order counter */}
            <div style={{ marginTop: 30, display: 'flex', gap: 26, alignItems: 'stretch' }}>
              {[0, 1].map((i) => {
                const p = beat(local, aMaybe - 0.4 + i * 0.9, 0.5);
                const empty = i === 1;
                return (
                  <div
                    key={i}
                    className="card"
                    style={{
                      flex: 1, padding: '26px 30px', opacity: 0.35 + 0.65 * p,
                      transform: `translateY(${(1 - p) * 26}px) scale(${0.9 + p * 0.1})`,
                      borderColor: empty ? 'rgba(255,255,255,0.08)' : 'rgba(0,255,136,0.45)',
                    }}
                  >
                    <div style={{ fontFamily: 'var(--font-mono)', fontSize: 14, color: '#7f95b5', letterSpacing: '0.2em' }}>
                      {empty ? 'ORDER #2' : 'ORDER #1'}
                    </div>
                    <div style={{ fontFamily: 'var(--font-display)', fontSize: 68, color: empty ? '#5b6b8c' : '#00ff88', textShadow: empty ? 'none' : '0 0 30px rgba(0,255,136,0.5)' }}>
                      {empty ? '?' : '1'}
                    </div>
                    <div style={{ color: '#9fb3d9', fontSize: 17 }}>
                      {empty ? '…if my mom gets excited 💕' : 'just paid · planners ×1'}
                    </div>
                  </div>
                );
              })}
            </div>

            {/* mom hearts */}
            {local > aMom - 0.5 &&
              [...Array(7)].map((_, i) => (
                <span
                  key={i}
                  style={{
                    position: 'absolute',
                    left: `${18 + i * 11}%`,
                    bottom: 0,
                    fontSize: 22 + (i % 3) * 10,
                    animation: `confetti-fall ${2.4 + (i % 3) * 0.6}s linear ${(i * 0.3).toFixed(2)}s infinite reverse`,
                    ['--drift' as string]: `${(i - 3) * 30}px`,
                  }}
                >
                  💕
                </span>
              ))}

            {/* thought bubble */}
            <Reveal at={aMaybe - 0.8} local={local} rise={24} style={{ position: 'absolute', right: 60, bottom: 34 }}>
              <div style={{ background: 'rgba(255,255,255,0.92)', color: '#122', borderRadius: 16, padding: '10px 20px', fontFamily: 'var(--font-hand)', fontSize: 27, transform: 'rotate(-2deg)' }}>
                one order… maybe two? 🤔
              </div>
            </Reveal>
          </div>
        </div>
      </Reveal>

      <div style={{ position: 'absolute', left: '50%', top: 52, transform: 'translateX(-50%)' }}>
        <PopWords text="refreshing… again" at={aRefresh - 0.5} local={local} size={40} color="#aef1ff" glow="rgba(0,229,255,0.7)" />
      </div>

      <div style={{ position: 'absolute', left: '50%', bottom: 60, transform: 'translateX(-50%)', width: 1340, background: 'rgba(3,6,14,0.75)', borderRadius: 16, padding: '14px 24px', border: '1px solid rgba(0,229,255,0.18)' }}>
        <SyncLine chunkIdx={chunkIdx} wordIdx={wordIdx} size={32} color="#dfeaff" activeColor="#00e5ff" />
      </div>
      <div className="grain abs-fill" />
    </div>
  );
}
