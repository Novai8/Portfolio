import { SceneProps, SyncLine, TypingText, PopWords, Reveal, anchorLocal } from './kit';
import { beat, clamp, hash } from '../lib/animationHelpers';

/**
 * SCENE 13 — "Escalation Emails"  (red alert system)
 * Thread stacks with timestamps, 14-minute countdown, calm reply drafting,
 * instant reply slam, icy edges, screen crack.
 */
export function Scene13({ active, local, chunkIdx, wordIdx }: SceneProps & { chunkIdx: number }) {
  if (!active) return <div className="scene-inner" />;
  const aAnother = anchorLocal(13, 'another');
  const aNoTrack = anchorLocal(13, 'notracking');
  const aFourteen = anchorLocal(13, 'fourteen');
  const aPolite = anchorLocal(13, 'polite');
  const aNoTime = anchorLocal(13, 'notime');
  const aCold = anchorLocal(13, 'cold');
  const aCountdown = anchorLocal(13, 'countdown');
  const end = 34.3;
  const crack = clamp((local - (end - 1.0)) / 1.0);

  const mins = Math.max(0, 14 - Math.max(0, local - aFourteen) * 2.4);
  const mm = Math.floor(mins);
  const ss = Math.floor((mins - mm) * 60);

  return (
    <div className="scene-inner">
      {/* red alert pulse */}
      <div
        className="abs-fill"
        style={{
          background: 'radial-gradient(80% 80% at 50% 40%, rgba(255,59,92,0.12), transparent 70%)',
          animation: 'breathe 1.6s ease-in-out infinite',
        }}
      />

      <div style={{ position: 'absolute', left: '50%', top: 40, transform: 'translateX(-50%)' }}>
        <PopWords text="then I get another email" at={aAnother} local={local} size={40} color="#ff5c7a" glow="rgba(255,59,92,0.6)" />
      </div>

      {/* timer */}
      <Reveal at={aFourteen - 0.5} local={local} rise={26} style={{ position: 'absolute', right: 120, top: 130 }}>
        <div className="card" style={{ padding: '20px 30px', borderColor: 'rgba(255,59,92,0.5)', background: 'rgba(20,2,8,0.7)', textAlign: 'center' }}>
          <div style={{ fontFamily: 'var(--font-mono)', fontSize: 13, letterSpacing: '0.3em', color: '#ff8fa3' }}>SINCE ORDER</div>
          <div style={{ fontFamily: 'var(--font-mono)', fontWeight: 700, fontSize: 64, color: '#ff4646', textShadow: '0 0 30px rgba(255,70,70,0.6)', marginTop: 4 }}>
            {mm.toString().padStart(2, '0')}:{ss.toString().padStart(2, '0')}
          </div>
          <div style={{ fontSize: 13, color: '#ff8fa3', fontFamily: 'var(--font-mono)' }}>and counting ⏱</div>
        </div>
      </Reveal>

      {/* thread */}
      <div style={{ position: 'absolute', left: 150, top: 150, width: 760, display: 'flex', flexDirection: 'column', gap: 20 }}>
        {/* incoming */}
        <div
          style={{
            transform: `translateX(${(1 - beat(local, aNoTrack - 0.5, 0.5)) * -320}px)`, opacity: beat(local, aNoTrack - 0.5, 0.35),
          }}
        >
          <div className="card" style={{ padding: '18px 26px', borderColor: 'rgba(255,59,92,0.5)', background: 'rgba(26,4,10,0.7)' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', fontFamily: 'var(--font-mono)', fontSize: 13, color: '#ff9db1' }}>
              <span>from: elliot graye</span><span>2:26 AM</span>
            </div>
            <div style={{ marginTop: 10, fontSize: 26, fontWeight: 900, color: '#ffdde3', animation: 'pulse-glow 1.1s infinite' }}>
              “Why no tracking yet?”
            </div>
          </div>
        </div>

        {/* calm outgoing */}
        <div style={{ transform: `translateX(${(1 - beat(local, aPolite - 0.3, 0.5)) * 320}px)`, opacity: beat(local, aPolite - 0.3, 0.35) }}>
          <div className="card" style={{ padding: '18px 26px', marginLeft: 90, borderColor: 'rgba(97,176,255,0.4)', background: 'rgba(6,12,22,0.7)' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', fontFamily: 'var(--font-mono)', fontSize: 13, color: '#9fc6ff' }}>
              <span>to: elliot graye</span><span style={{ color: '#7dd8a8' }}>✍ drafting calmly…</span>
            </div>
            <div style={{ marginTop: 10, fontSize: 18.5, color: '#cfe4ff', lineHeight: 1.55 }}>
              <TypingText
                text="“Hi! For high-volume orders, we confirm shipping details for security…”"
                at={aPolite + 0.3}
                dur={1.8}
                local={local}
              />
            </div>
          </div>
        </div>

        {/* instant slam */}
        {local > aNoTime - 0.6 && (() => {
          const p = beat(local, aNoTime - 0.6, 0.3);
          const wob = local < aNoTime + 1.2 ? 1 : 0;
          return (
            <div
              className={wob ? 'shake-hard' : undefined}
              style={{ transform: `scale(${0.6 + 0.4 * p})`, opacity: p }}
            >
              <div className="card" style={{ padding: '18px 26px', borderColor: '#ff4646', background: 'rgba(48,0,10,0.85)', boxShadow: '0 0 70px rgba(255,70,70,0.4)' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontFamily: 'var(--font-mono)', fontSize: 13, color: '#ff9db1' }}>
                  <span>from: elliot graye</span><span style={{ color: '#ff4646' }}>INSTANT ⚡</span>
                </div>
                <div style={{ marginTop: 10, fontSize: 30, fontWeight: 900, color: '#fff', textShadow: '0 0 26px rgba(255,70,70,0.8)' }}>
                  “No time. <span style={{ animation: 'pulse-glow 0.5s infinite', color: '#ff4646' }}>Ship now. I paid.</span>”
                </div>
              </div>
            </div>
          );
        })()}
      </div>

      {/* cold hands / countdown */}
      {local > aCold - 0.4 && (
        <div style={{ position: 'absolute', left: '50%', bottom: 240, transform: 'translateX(-50%)', textAlign: 'center' }}>
          <div style={{ fontFamily: 'var(--font-hand)', fontSize: 40, color: '#bfe4ff' }}>
            now my hands are cold 🥶
          </div>
          {local > aCountdown - 0.2 && (
            <div style={{ fontFamily: 'var(--font-display)', fontSize: 46, color: '#fff', letterSpacing: '0.14em', textShadow: '0 0 30px rgba(97,176,255,0.8)', animation: 'pulse-glow 0.8s infinite' }}>
              THAT'S NOT A CUSTOMER. THAT'S A <span style={{ color: '#61b0ff' }}>COUNTDOWN.</span>
            </div>
          )}
        </div>
      )}

      {/* icy edges */}
      {local > aCold && (
        <div
          className="abs-fill"
          style={{
            boxShadow: `inset 0 0 ${120 + Math.sin(local * 2) * 40}px rgba(160,220,255,0.55)`,
            background: 'radial-gradient(120% 120% at 50% 50%, transparent 55%, rgba(190,230,255,0.14) 100%)',
          }}
        />
      )}

      <div style={{ position: 'absolute', left: '50%', bottom: 60, transform: 'translateX(-50%)', width: 1320, background: 'rgba(8,2,6,0.82)', borderRadius: 16, padding: '14px 24px', border: '1px solid rgba(255,59,92,0.3)' }}>
        <SyncLine chunkIdx={chunkIdx} wordIdx={wordIdx} size={30} color="#ffe0e6" activeColor="#ff4646" />
      </div>

      {/* glass crack */}
      {crack > 0 && (
        <svg className="abs-fill" width="1600" height="900" style={{ opacity: crack }}>
          {[
            'M 800 450 L 500 180 L 420 60', 'M 800 450 L 1150 220 L 1260 80',
            'M 800 450 L 460 700 L 340 850', 'M 800 450 L 1120 680 L 1240 860',
            'M 800 450 L 800 40', 'M 800 450 L 250 420 L 60 380', 'M 800 450 L 1360 470 L 1560 520',
          ].map((d, i) => (
            <path key={i} d={d} stroke="rgba(255,255,255,0.85)" strokeWidth={2.4} fill="none" strokeDasharray="900" strokeDashoffset={900 * (1 - clamp(crack * 1.6 - i * 0.08))} style={{ filter: 'drop-shadow(0 0 6px rgba(255,255,255,0.6))' }} />
          ))}
          {['M 500 180 L 470 240 L 540 250'].map((d, i) => (
            <path key={`b${i}`} d={d} stroke="rgba(255,255,255,0.5)" strokeWidth={1.6} fill="none" />
          ))}
        </svg>
      )}
      <div className="grain abs-fill" />
      {void hash}
    </div>
  );
}
