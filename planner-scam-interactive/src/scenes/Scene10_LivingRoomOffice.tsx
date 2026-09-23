import { SceneProps, SyncLine, PopWords, Reveal, anchorLocal } from './kit';
import { beat, clamp, pingpong } from '../lib/animationHelpers';

/**
 * SCENE 10 — "Living Room Office"  (isometric top-down apartment)
 * LIVING = OFFICE = DINING blueprint labels, furniture morph, vintage phone
 * ringing with waves, pacing loop, zoom into the phone.
 */
export function Scene10({ active, local, chunkIdx, wordIdx }: SceneProps & { chunkIdx: number }) {
  if (!active) return <div className="scene-inner" />;
  const aWalk = anchorLocal(10, 'walk');
  const aDanger = anchorLocal(10, 'danger');
  const aMaya = anchorLocal(10, 'maya');
  const aRing = anchorLocal(10, 'ring');
  const end = 14.5;
  const zoom = clamp((local - (end - 0.9)) / 0.9);
  const pacing = pingpong(local, 3.4);

  return (
    <div className="scene-inner" style={{ transform: `scale(${1 + zoom * 1.4}) translateY(${zoom * 180}px)`, transformOrigin: '54% 60%' }}>
      {/* iso floor */}
      <div
        className="abs-fill"
        style={{
          background: 'linear-gradient(160deg,#0e1830,#0a1020)',
          transform: 'perspective(1400px) rotateX(38deg) scale(1.35)',
          transformOrigin: '50% 70%',
        }}
      >
        <div
          className="abs-fill"
          style={{
            backgroundImage:
              'linear-gradient(rgba(122,208,255,0.13) 1.5px, transparent 1.5px), linear-gradient(90deg, rgba(122,208,255,0.13) 1.5px, transparent 1.5px)',
            backgroundSize: '90px 90px',
            animation: 'grid-pan 5s linear infinite',
          }}
        />
      </div>

      {/* room cards: LIVING = OFFICE = DINING */}
      <div style={{ position: 'absolute', left: '50%', top: 80, transform: 'translateX(-50%)', display: 'flex', gap: 26, alignItems: 'center' }}>
        {['LIVING', 'OFFICE', 'DINING'].map((r, i) => {
          const p = beat(local, aWalk + 0.3 + i * 0.55, 0.5);
          return (
            <div key={r} style={{ display: 'flex', alignItems: 'center', gap: 26 }}>
              <div
                style={{
                  border: '3px dashed #7ad0ff', color: '#bfe8ff', padding: '14px 30px', borderRadius: 14,
                  fontFamily: 'var(--font-display)', fontSize: 30, letterSpacing: '0.14em',
                  background: 'rgba(10,20,40,0.5)',
                  opacity: 0.25 + 0.75 * p,
                  transform: `translateY(${(1 - p) * -30}px) scale(${0.8 + 0.2 * p})`,
                  boxShadow: p > 0.9 ? '0 0 34px rgba(122,208,255,0.35)' : undefined,
                }}
              >
                {r}
              </div>
              {i < 2 && <span style={{ fontFamily: 'var(--font-display)', fontSize: 44, color: '#7ad0ff', opacity: beat(local, aWalk + 0.6 + i * 0.55, 0.4) }}>=</span>}
            </div>
          );
        })}
      </div>

      {/* furniture morph */}
      <Reveal at={aWalk + 1.2} local={local} rise={20} style={{ position: 'absolute', left: 300, top: 420 }}>
        <div style={{ position: 'relative', width: 300, height: 240 }}>
          <div style={{ position: 'absolute', inset: 0, display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 130, opacity: 1 - Math.min(1, Math.max(0, (local - aWalk - 1.4) / 0.9)), transform: `rotate(${Math.sin(local) * 3}deg)` }}>
            🛋️
          </div>
          <div style={{ position: 'absolute', inset: 0, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', fontSize: 120, opacity: Math.min(1, Math.max(0, (local - aWalk - 1.4) / 0.9)) }}>
            💻
            <div style={{ fontSize: 70 }}>🪑</div>
          </div>
          <div style={{ textAlign: 'center', fontFamily: 'var(--font-hand)', fontSize: 28, color: '#9fd8ff', marginTop: 6 }}>
            couch → desk
          </div>
        </div>
      </Reveal>

      {/* dining = office table */}
      <Reveal at={aWalk + 1.8} local={local} rise={20} style={{ position: 'absolute', right: 240, top: 430 }}>
        <div style={{ textAlign: 'center', animation: 'floaty-soft 3.4s ease-in-out infinite' }}>
          <div style={{ fontSize: 110 }}>🍝</div>
          <div style={{ fontFamily: 'var(--font-hand)', fontSize: 26, color: '#9fd8ff' }}>dining = desk</div>
        </div>
      </Reveal>

      {/* pacing character */}
      <div style={{ position: 'absolute', left: 760 + Math.sin(pacing * Math.PI * 2) * 190, top: 640, fontSize: 60, transform: `scaleX(${pacing > 0.5 ? -1 : 1})`, filter: 'drop-shadow(0 10px 20px rgba(0,0,0,0.5))' }}>
        🚶
      </div>
      <div style={{ position: 'absolute', left: 700, top: 720, width: 500, height: 60, border: '3px dashed rgba(122,208,255,0.3)', borderRadius: 40 }} />

      {/* vintage phone */}
      <Reveal at={aDanger} local={local} rise={30} style={{ position: 'absolute', left: '50%', top: 300, transform: 'translateX(-50%)' }}>
        <div style={{ textAlign: 'center', animation: 'shake-hard 0.9s linear infinite' }}>
          {[0, 1, 2].map((i) => (
            <span
              key={i}
              style={{
                position: 'absolute', left: '50%', top: '50%', width: 190, height: 190, margin: '-95px 0 0 -95px',
                borderRadius: '50%', border: '3px solid rgba(122,208,255,0.5)',
                animation: `ring-wave 1.4s ease-out ${i * 0.45}s infinite`,
              }}
            />
          ))}
          <div style={{ fontSize: 120, display: 'inline-block' }}>☎️</div>
          <div style={{ fontFamily: 'var(--font-mono)', color: '#7ad0ff', letterSpacing: '0.3em', fontSize: 16, marginTop: 8 }}>
            RING RING RING
          </div>
        </div>
      </Reveal>

      <div style={{ position: 'absolute', left: '50%', top: 170, transform: 'translateX(-50%)' }}>
        <PopWords text="living room = office = dining room" at={aWalk} local={local} size={38} color="#bfe8ff" />
      </div>

      <div style={{ position: 'absolute', left: '50%', bottom: 46, transform: 'translateX(-50%)', width: 1280, background: 'rgba(5,10,22,0.82)', borderRadius: 16, padding: '14px 24px', border: '1px solid rgba(122,208,255,0.2)' }}>
        <SyncLine chunkIdx={chunkIdx} wordIdx={wordIdx} size={30} color="#dfeaff" activeColor="#7ad0ff" />
      </div>
      <div className="grain abs-fill" />
    </div>
  );
}
