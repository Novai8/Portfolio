import { SceneProps, SyncLine, PopWords, Reveal, Counter, CheckRow, anchorLocal } from './kit';
import { beat, clamp } from '../lib/animationHelpers';

/**
 * SCENE 18 — "Happy Ending"  (sunrise success story)
 * Legit business card flip, "real" checklist, reorder counter, growth chart,
 * upgrade moment, raccoon callback, moral card, SHIP YOUR SPINE FIRST.
 */
export function Scene18({ active, local, chunkIdx, wordIdx }: SceneProps & { chunkIdx: number }) {
  if (!active) return <div className="scene-inner" />;
  const aHop = anchorLocal(18, 'hop');
  const aReal = anchorLocal(18, 'real');
  const aDoor = anchorLocal(18, 'frontdoor');
  const aFulfill = anchorLocal(18, 'fulfill');
  const aReorder = anchorLocal(18, 'reorder');
  const aUpgraded = anchorLocal(18, 'upgraded');
  const aRules = anchorLocal(18, 'rules');
  const aJoke = anchorLocal(18, 'warehousejoke');
  const aNearMiss = anchorLocal(18, 'nearmiss');
  const aEver = anchorLocal(18, 'everget');
  const aDontShip = anchorLocal(18, 'dontship');
  const aSpine = anchorLocal(18, 'spine');
  const end = 85.2;
  const outro = clamp((local - (end - 2.2)) / 2.2);

  return (
    <div className="scene-inner" style={{ filter: `brightness(${1 - outro * 0.55})` }}>
      {/* rising sun */}
      <div
        style={{
          position: 'absolute', left: '50%', bottom: -260, transform: 'translateX(-50%)',
          width: 720, height: 720, borderRadius: '50%',
          background: 'radial-gradient(circle at 50% 30%, #fff3c4, #ffca6a 55%, #ff9a3c)',
          opacity: 0.5, animation: 'breathe 5s ease-in-out infinite',
        }}
      />

      {/* legit business card flip */}
      <Reveal at={aHop} local={local} rise={30} style={{ position: 'absolute', left: '50%', top: 90, transform: 'translateX(-50%)', perspective: 900 }}>
        <div
          style={{
            transform: `rotateY(${beat(local, aHop + 0.2, 0.9) * 360}deg)`,
            transformStyle: 'preserve-3d',
            background: 'linear-gradient(135deg,#ffffff,#ffe9c9)',
            borderRadius: 20, padding: '20px 44px',
            boxShadow: '0 30px 80px rgba(60,20,0,0.35)',
            textAlign: 'center', color: '#23262e',
          }}
        >
          <div style={{ fontFamily: 'var(--font-mono)', fontSize: 13, letterSpacing: '0.25em', color: '#b0793a' }}>NEW CUSTOMER · VERIFIED</div>
          <div style={{ fontFamily: 'var(--font-display)', fontSize: 34, marginTop: 6 }}>🏙️ Downtown Coworking Co.</div>
          <div style={{ fontFamily: 'var(--font-hand)', fontSize: 27, color: '#0e9f6e' }}>they laughed at my jokes · they have a FRONT DOOR</div>
        </div>
      </Reveal>

      {/* real checklist */}
      <Reveal at={aReal} local={local} rise={26} style={{ position: 'absolute', left: 120, top: 260 }}>
        <div className="card" style={{ width: 430, padding: '24px 30px', background: 'rgba(255,252,244,0.9)', color: '#23262e' }}>
          <div style={{ fontFamily: 'var(--font-mono)', fontSize: 13, letterSpacing: '0.25em', color: '#b0793a', marginBottom: 12 }}>HOW TO SPOT A REAL CUSTOMER</div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
            <CheckRow label="a website" at={aReal + 0.4} local={local} size={23} color="#23262e" />
            <CheckRow label="a phone number" at={aReal + 1.0} local={local} size={23} color="#23262e" />
            <CheckRow label="a normal address" at={aDoor - 1.6} local={local} size={23} color="#23262e" />
            <CheckRow label="a front door 🚪" at={aDoor - 0.6} local={local} size={23} color="#23262e" />
          </div>
        </div>
      </Reveal>

      {/* order + reorder */}
      <Reveal at={aFulfill} local={local} rise={26} style={{ position: 'absolute', right: 130, top: 260 }}>
        <div className="card" style={{ width: 430, padding: '24px 30px', textAlign: 'center', background: 'rgba(6,20,14,0.82)', borderColor: 'rgba(0,255,136,0.4)' }}>
          <div style={{ fontFamily: 'var(--font-mono)', fontSize: 12.5, letterSpacing: '0.25em', color: '#7dd8a8' }}>BRANDED PLANNERS · FULFILLED</div>
          <div style={{ margin: '10px 0' }}>
            <Counter target={200} at={aFulfill + 0.2} dur={1.4} local={local} size={72} color="#00ff88" suffix=" 📦" />
          </div>
          <div style={{ height: 10, borderRadius: 6, background: 'rgba(255,255,255,0.12)', overflow: 'hidden' }}>
            <div style={{ width: `${beat(local, aFulfill + 0.2, 1.4) * 100}%`, height: '100%', background: '#00ff88', boxShadow: '0 0 14px #00ff88aa' }} />
          </div>
          {local > aReorder - 0.3 && (
            <div style={{ marginTop: 12, fontFamily: 'var(--font-display)', fontSize: 22, color: '#ffd35c', animation: 'pulse-glow 1.6s infinite' }}>
              🔁 reorder next month ✓
            </div>
          )}
        </div>
      </Reveal>

      {/* the twist: upgraded */}
      {local > aUpgraded - 0.5 && (
        <div style={{ position: 'absolute', left: '50%', top: 330, transform: `translateX(-50%) scale(${0.6 + 0.4 * beat(local, aUpgraded - 0.5, 0.6)})`, opacity: beat(local, aUpgraded - 0.5, 0.4), textAlign: 'center', width: 1200 }}>
          <div style={{ fontFamily: 'var(--font-display)', fontSize: 92, color: '#fff', textShadow: '0 0 60px rgba(255,202,106,0.8), 0 10px 0 rgba(120,60,10,0.35)' }}>
            IT <span style={{ color: '#ffd35c' }}>UPGRADED</span> ME.
          </div>
          <div style={{ fontFamily: 'var(--font-hand)', fontSize: 32, color: '#ffe9c9', marginTop: 6 }}>
            “if fraudsters target you… you built something real enough to be worth targeting.”
          </div>
        </div>
      )}

      {/* growth chart */}
      <Reveal at={aRules - 0.3} local={local} rise={26} style={{ position: 'absolute', left: '50%', top: 500, transform: 'translateX(-50%)' }}>
        <div className="card" style={{ width: 760, padding: '20px 30px 14px', background: 'rgba(8,10,20,0.75)' }}>
          <div style={{ fontFamily: 'var(--font-mono)', fontSize: 12.5, letterSpacing: '0.25em', color: '#9fc6ff', marginBottom: 6 }}>
            SECURITY RULES · PLAIN ENGLISH · VERIFYING REALITY
          </div>
          <svg width="700" height="130" viewBox="0 0 700 130">
            <path
              d="M 10 115 C 120 112, 180 100, 250 88 C 330 74, 380 66, 440 46 C 520 20, 600 16, 690 8"
              stroke="#00ff88" strokeWidth={5} fill="none"
              strokeDasharray="760" strokeDashoffset={760 * (1 - clamp((local - aRules) / 2.2))}
              style={{ filter: 'drop-shadow(0 0 10px rgba(0,255,136,0.6))' }}
            />
            <circle cx="690" cy="8" r={7} fill="#ffd35c" opacity={clamp((local - aRules) / 2.4)} style={{ filter: 'drop-shadow(0 0 12px #ffd35c)' }} />
          </svg>
        </div>
      </Reveal>

      {/* raccoon callback */}
      {local > aJoke - 0.4 && (
        <div style={{ position: 'absolute', left: 150, bottom: 250, opacity: beat(local, aJoke - 0.4, 0.4), transform: 'rotate(-5deg)', animation: 'floaty-soft 3s ease-in-out infinite' }}>
          <div className="card" style={{ padding: '14px 22px', background: 'rgba(255,255,255,0.9)', color: '#23262e', width: 360 }}>
            <div style={{ fontSize: 40, textAlign: 'center' }}>🦝🎩💰</div>
            <div style={{ fontFamily: 'var(--font-hand)', fontSize: 25, textAlign: 'center' }}>
              “almost donated $12,000 of planners to a raccoon warehouse”
            </div>
          </div>
        </div>
      )}

      {/* moral card */}
      {local > aNearMiss - 0.4 && (
        <div style={{ position: 'absolute', right: 140, bottom: 250, opacity: beat(local, aNearMiss - 0.4, 0.5), transform: 'rotate(1.6deg)' }}>
          <div className="card" style={{ width: 470, padding: '22px 30px', background: 'linear-gradient(150deg,#fff8ea,#ffe9c9)', color: '#4a2c10', boxShadow: '0 30px 70px rgba(60,20,0,0.35)' }}>
            <div style={{ fontFamily: 'var(--font-mono)', fontSize: 12, letterSpacing: '0.3em', color: '#b0793a', marginBottom: 8 }}>THE MORAL</div>
            <div style={{ fontFamily: 'var(--font-display)', fontSize: 25, lineHeight: 1.4 }}>
              Wins feel amazing. <span style={{ color: '#c2570f' }}>Near-misses</span> are where you become the person who can handle the wins.
            </div>
          </div>
        </div>
      )}

      {/* final warning + punchline */}
      {local > aEver - 0.6 && (
        <div style={{ position: 'absolute', left: '50%', bottom: 100, transform: 'translateX(-50%)', textAlign: 'center', width: 1300 }}>
          <div style={{ fontFamily: 'var(--font-hand)', fontSize: 36, color: '#ffe9c9', opacity: beat(local, aEver - 0.6, 0.4), textShadow: '0 4px 30px rgba(255,150,60,0.5)' }}>
            if you ever get a massive order at 2:07 a.m. to an abandoned warehouse…
          </div>
          {local > aDontShip - 0.3 && (
            <div
              style={{
                marginTop: 8, fontFamily: 'var(--font-display)', fontSize: 78, color: '#ff4646',
                textShadow: '0 0 50px rgba(255,70,70,0.55)',
                transform: `scale(${1 + 0.25 * beat(local, aDontShip - 0.3, 0.25) * (1 - beat(local, aDontShip - 0.3, 0.6))})`,
              }}
            >
              DON'T SHIP IT.
            </div>
          )}
          {local > aSpine - 0.4 && (
            <div style={{ marginTop: 6, fontFamily: 'var(--font-display)', fontSize: 96, color: '#fff', letterSpacing: '0.02em', textShadow: '0 0 70px rgba(0,255,136,0.5)', transform: `scale(${0.5 + 0.5 * beat(local, aSpine - 0.4, 0.35)})` }}>
              SHIP YOUR <span style={{ color: '#00ff88' }}>SPINE</span> FIRST. 🦴
            </div>
          )}
        </div>
      )}

      <div style={{ position: 'absolute', left: '50%', top: 48, transform: 'translateX(-50%)' }}>
        <PopWords text="we hop on a call — they're REAL" at={aHop - 0.2} local={local} size={36} color="#ffe9c9" glow="rgba(255,202,106,0.5)" />
      </div>

      <div style={{ position: 'absolute', left: '50%', bottom: 16, transform: 'translateX(-50%)', width: 1340, background: 'rgba(20,10,2,0.78)', borderRadius: 16, padding: '12px 24px', border: '1px solid rgba(255,202,106,0.3)', opacity: 1 - outro }}>
        <SyncLine chunkIdx={chunkIdx} wordIdx={wordIdx} size={29} color="#fff3d6" activeColor="#ffca6a" />
      </div>
      <div className="grain abs-fill" />
    </div>
  );
}
