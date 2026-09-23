import { SceneProps, SyncLine, PopWords, Reveal, anchorLocal } from './kit';
import { beat, clamp, hash } from '../lib/animationHelpers';

/**
 * SCENE 14 — "Payment Call"  (customer-service UI, hold-music visualizer)
 * Call timer, drooping sad notes, rep avatar, HIGH RISK badge, rising temp
 * gauge, fade-to-black OUT.
 */
export function Scene14({ active, local, chunkIdx, wordIdx }: SceneProps & { chunkIdx: number }) {
  if (!active) return <div className="scene-inner" />;
  const aStand = anchorLocal(14, 'stand');
  const aSerenade = anchorLocal(14, 'serenade');
  const aRep = anchorLocal(14, 'rep');
  const aHighRisk = anchorLocal(14, 'highrisk');
  const aScam = anchorLocal(14, 'scam');
  const aBetrayed = anchorLocal(14, 'betrayed');
  const end = 53.1;
  const fade = clamp((local - (end - 1.1)) / 1.1);

  const callSecs = Math.max(0, local - (aSerenade - 1.2));
  const mm = Math.floor(callSecs / 60);
  const ss = Math.floor(callSecs % 60);

  return (
    <div className="scene-inner">
      {/* call window */}
      <Reveal at={aStand} local={local} rise={36} style={{ position: 'absolute', left: '50%', top: 110, transform: 'translateX(-50%)' }}>
        <div className="card" style={{ width: 640, padding: '30px 40px', textAlign: 'center', background: 'rgba(6,14,26,0.88)', borderColor: 'rgba(97,176,255,0.35)' }}>
          <div style={{ width: 120, height: 120, margin: '0 auto', borderRadius: '50%', background: 'linear-gradient(135deg,#61b0ff,#7a5cff)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 60, position: 'relative' }}>
            🎧
            <span style={{ position: 'absolute', inset: -10, borderRadius: '50%', border: '3px solid rgba(97,176,255,0.5)', animation: 'ring-wave 1.8s ease-out infinite' }} />
            <span style={{ position: 'absolute', inset: -10, borderRadius: '50%', border: '3px solid rgba(97,176,255,0.4)', animation: 'ring-wave 1.8s ease-out 0.6s infinite' }} />
          </div>
          <div style={{ fontFamily: 'var(--font-display)', fontSize: 30, color: '#dfeaff', marginTop: 14 }}>PAYMENT PROCESSOR SUPPORT</div>
          <div style={{ fontFamily: 'var(--font-mono)', color: '#8fd3ff', fontSize: 20, marginTop: 6, letterSpacing: '0.16em' }}>
            {isFinite(mm) ? `${mm.toString().padStart(2, '0')}:${ss.toString().padStart(2, '0')}` : '00:00'} · on hold 🎵
          </div>

          {/* hold music visualizer — sad drooping bars */}
          <div style={{ display: 'flex', gap: 10, justifyContent: 'center', alignItems: 'flex-end', height: 90, marginTop: 20 }}>
            {[...Array(12)].map((_, i) => {
              const droop = Math.abs(Math.sin(local * 1.1 + i * 0.7));
              const h = 12 + droop * 66;
              return (
                <div key={i} style={{ width: 16, height: h, borderRadius: 6, background: 'linear-gradient(180deg,#61b0ff,#2b4a8f)', opacity: 0.75, transform: `rotate(${(hash(i) - 0.5) * 10}deg)`, transformOrigin: 'bottom' }} />
              );
            })}
          </div>
          <div style={{ display: 'flex', gap: 14, justifyContent: 'center', marginTop: 8, fontSize: 30 }}>
            {['🎵', '🎶', '🎵'].map((n, i) => (
              <span key={i} style={{ animation: `floaty ${2.2 + i * 0.4}s ease-in-out ${i * 0.4}s infinite`, transform: 'rotate(180deg)', opacity: 0.75 }}>
                {n}
              </span>
            ))}
          </div>
        </div>
      </Reveal>

      {/* rep answer */}
      {local > aRep - 0.4 && (
        <Reveal at={aRep - 0.4} local={local} rise={26} style={{ position: 'absolute', left: 130, bottom: 240 }}>
          <div className="card" style={{ width: 430, padding: '20px 26px', background: 'rgba(8,20,14,0.8)', borderColor: 'rgba(125,216,168,0.4)' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 14 }}>
              <span style={{ fontSize: 44 }}>🧑‍💼</span>
              <div style={{ textAlign: 'left' }}>
                <div style={{ color: '#d9ffe9', fontWeight: 700, fontSize: 20 }}>Support Rep</div>
                <div style={{ color: '#7dd8a8', fontFamily: 'var(--font-mono)', fontSize: 13 }}>“I can't confirm details… but…”</div>
              </div>
            </div>
          </div>
        </Reveal>
      )}

      {/* HIGH RISK badge + temp gauge */}
      {local > aHighRisk - 0.5 && (
        <>
          <div style={{ position: 'absolute', right: 150, top: 160, textAlign: 'center' }}>
            <div
              style={{
                border: '6px solid #ffd35c', background: 'rgba(40,26,0,0.55)', color: '#ffd35c',
                fontFamily: 'var(--font-display)', fontSize: 44, padding: '12px 28px', borderRadius: 14,
                letterSpacing: '0.1em', transform: 'rotate(6deg)',
                animation: 'pulse-glow 1.1s infinite', boxShadow: '0 0 70px rgba(255,211,92,0.4)',
              }}
            >
              ⚠ HIGH RISK
            </div>
            <div style={{ marginTop: 22, display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 8 }}>
              <div style={{ width: 34, height: 190, borderRadius: 20, border: '3px solid rgba(255,255,255,0.25)', position: 'relative', overflow: 'hidden', background: 'rgba(255,255,255,0.05)' }}>
                <div
                  style={{
                    position: 'absolute', bottom: 0, width: '100%',
                    height: `${clamp((local - aHighRisk + 0.5) / 3) * 100}%`,
                    background: 'linear-gradient(180deg,#ff4646,#ffd35c,#7dd8a8)',
                    transition: 'height 0.2s linear',
                  }}
                />
              </div>
              <div style={{ fontFamily: 'var(--font-mono)', fontSize: 12.5, color: '#ffb3b3', letterSpacing: '0.2em' }}>TEMPERATURE</div>
            </div>
          </div>
        </>
      )}

      {/* sinking realization */}
      {local > aScam - 0.4 && (
        <div
          style={{
            position: 'absolute', left: '50%', bottom: 250, transform: `translateX(-50%) translateY(${clamp((local - aScam + 0.4) / 2) * 26}px)`,
            opacity: clamp((local - aScam + 0.4) * 2) * (1 - fade),
            fontFamily: 'var(--font-display)', fontSize: 64, color: '#ff5c5c',
            textShadow: '0 18px 50px rgba(255,70,70,0.4)', whiteSpace: 'nowrap',
          }}
        >
          “So… scam.”
        </div>
      )}

      <div style={{ position: 'absolute', left: '50%', top: 44, transform: 'translateX(-50%)' }}>
        <PopWords text="I call the payment processor" at={aStand} local={local} size={36} color="#9fc6ff" />
      </div>

      <div style={{ position: 'absolute', left: '50%', bottom: 56, transform: 'translateX(-50%)', width: 1320, background: 'rgba(3,7,14,0.82)', borderRadius: 16, padding: '14px 24px', border: '1px solid rgba(97,176,255,0.25)', opacity: 1 - fade }}>
        <SyncLine chunkIdx={chunkIdx} wordIdx={wordIdx} size={30} color="#d5e6ff" activeColor="#61b0ff" />
      </div>

      {/* fade to black OUT */}
      <div className="abs-fill" style={{ background: '#000', opacity: fade }} />
      <div className="grain abs-fill" />
    </div>
  );
}
