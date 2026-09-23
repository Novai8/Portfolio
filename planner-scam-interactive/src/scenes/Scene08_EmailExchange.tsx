import { SceneProps, SyncLine, TypingText, Reveal, anchorLocal } from './kit';
import { beat, hash } from '../lib/animationHelpers';

/**
 * SCENE 08 — "Email Exchange"  (animated dark-mode inbox)
 * Outgoing email typing, typing dots, replies sliding in with urgent badges,
 * timestamp counter, glitch corruption at the end.
 */
export function Scene08({ active, local, chunkIdx, wordIdx }: SceneProps & { chunkIdx: number }) {
  if (!active) return <div className="scene-inner" />;
  const aEmail = anchorLocal(8, 'email');
  const aFivemin = anchorLocal(8, 'fivemin');
  const aReply = anchorLocal(8, 'reply');
  const aTracking = anchorLocal(8, 'tracking');
  const end = 26.4;
  const glitch = Math.max(0, (local - (end - 0.8)) / 0.8);

  return (
    <div className="scene-inner" style={{ filter: `hue-rotate(${glitch * 40}deg)` }}>
      {/* inbox chrome */}
      <div className="abs-fill" style={{ background: 'linear-gradient(150deg,#0d1424,#070a12)' }} />
      <Reveal at={0.2} local={local} rise={20} style={{ position: 'absolute', left: 110, top: 120, right: 110, bottom: 210 }}>
        <div className="card" style={{ height: '100%', padding: '26px 34px', background: 'rgba(8,11,20,0.85)', overflow: 'hidden' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 16, borderBottom: '1px solid rgba(255,255,255,0.08)', paddingBottom: 16 }}>
            <span style={{ fontFamily: 'var(--font-display)', fontSize: 26, color: '#dfe6ff' }}>📥 Inbox</span>
            <span className="pill" style={{ background: 'rgba(92,139,255,0.16)', borderColor: 'rgba(92,139,255,0.4)', color: '#a7c1ff', fontSize: 13 }}>
              elliot graye thread · {Math.max(1, Math.floor(local))} messages
            </span>
            <div style={{ flex: 1 }} />
            <div style={{ display: 'flex', gap: 7 }}>
              {[0, 1, 2].map((i) => (
                <span key={i} style={{ width: 10, height: 10, borderRadius: '50%', background: '#5c8bff', animation: `typing-dot 1.1s ease-in-out ${i * 0.18}s infinite` }} />
              ))}
            </div>
          </div>

          {/* outgoing */}
          <div style={{ marginTop: 24, transform: `perspective(900px) rotateY(-4deg) translateX(${(1 - beat(local, aEmail - 0.2, 0.5)) * 260}px)`, opacity: beat(local, aEmail - 0.2, 0.35) }}>
            <div className="card" style={{ padding: '18px 24px', marginLeft: 120, borderColor: 'rgba(0,255,136,0.3)' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', color: '#9fb3d9', fontSize: 13.5, fontFamily: 'var(--font-mono)' }}>
                <span>to: elliot graye ✔</span>
                <span>2:11 AM</span>
              </div>
              <div style={{ marginTop: 10, fontSize: 20, color: '#e8ecff', lineHeight: 1.5, minHeight: 56 }}>
                <TypingText text="Hey Elliot! Huge thanks for your order—just confirming delivery details for such a large shipment." at={aEmail + 0.3} dur={2.2} local={local} />
              </div>
            </div>
          </div>

          {/* five minutes later */}
          {local > aFivemin - 0.6 && (
            <div style={{ textAlign: 'center', margin: '18px 0', opacity: beat(local, aFivemin - 0.6, 0.4) }}>
              <span className="pill" style={{ color: '#ffd76a', borderColor: 'rgba(255,215,106,0.4)', background: 'rgba(255,215,106,0.08)', fontSize: 13 }}>
                ⏱ 5 MINUTES LATER
              </span>
            </div>
          )}

          {/* reply 1 */}
          <div style={{ transform: `perspective(900px) rotateY(4deg) translateX(${(1 - beat(local, aFivemin - 0.1, 0.45)) * -300}px)`, opacity: beat(local, aFivemin - 0.1, 0.3) }}>
            <div className="card" style={{ padding: '18px 24px', marginRight: 160, borderColor: 'rgba(255,70,70,0.45)', position: 'relative', background: 'rgba(30,8,12,0.6)' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', color: '#ff9db1', fontSize: 13.5, fontFamily: 'var(--font-mono)' }}>
                <span>from: elliot graye</span>
                <span style={{ color: '#ff4646' }}>received · now</span>
              </div>
              <div style={{ marginTop: 10, fontSize: 22, fontWeight: 700, color: '#ffe3e9' }}>
                “Ship ASAP. Need by Friday. <span style={{ color: '#ff4646' }}>Don't call. Busy.</span>”
              </div>
              <span style={{ position: 'absolute', top: -12, right: 18, background: '#ff4646', color: '#fff', fontSize: 12, fontWeight: 900, borderRadius: 8, padding: '4px 10px', letterSpacing: '0.1em', boxShadow: '0 0 22px rgba(255,70,70,0.7)', animation: 'pulse-glow 1.2s infinite' }}>
                URGENT
              </span>
            </div>
          </div>

          {/* reply 2 */}
          {local > aTracking - 1.2 && (
            <div style={{ marginTop: 18, transform: `perspective(900px) rotateY(4deg) translateX(${(1 - beat(local, aTracking - 0.9, 0.45)) * -300}px)`, opacity: beat(local, aTracking - 0.9, 0.3) }}>
              <div className="card" style={{ padding: '18px 24px', marginRight: 160, borderColor: 'rgba(255,70,70,0.7)', background: 'rgba(40,4,10,0.75)' }}>
                <div style={{ fontSize: 22, fontWeight: 900, color: '#ff5c5c', textShadow: '0 0 22px rgba(255,70,70,0.6)', transform: `scale(${1 + 0.05 * Math.sin(local * 7)})`, transformOrigin: 'left' }}>
                  “Also send tracking <span style={{ textDecoration: 'underline' }}>immediately</span>.”
                </div>
              </div>
            </div>
          )}
        </div>
      </Reveal>

      {/* floating mail icons */}
      {[...Array(6)].map((_, i) => (
        <span
          key={i}
          style={{
            position: 'absolute', left: `${6 + i * 16}%`, top: `${8 + hash(i) * 12}%`,
            fontSize: 26 + hash(i + 2) * 18, opacity: 0.16 + 0.1 * Math.sin(local * 2 + i),
            animation: `floaty ${3 + i * 0.4}s ease-in-out ${i * 0.3}s infinite`,
          }}
        >
          ✉️
        </span>
      ))}

      <div style={{ position: 'absolute', left: '50%', top: 48, transform: 'translateX(-50%)' }}>
        <span style={{ fontFamily: 'var(--font-display)', fontSize: 38, color: '#a7c1ff', textShadow: '0 0 30px rgba(92,139,255,0.5)' }}>
          I email the customer.
        </span>
      </div>

      <div style={{ position: 'absolute', left: '50%', bottom: 84, transform: 'translateX(-50%)', width: 1340, background: 'rgba(4,7,14,0.8)', borderRadius: 16, padding: '14px 24px', border: '1px solid rgba(92,139,255,0.22)' }}>
        <SyncLine chunkIdx={chunkIdx} wordIdx={wordIdx} size={31} color="#dfe6ff" activeColor="#5c8bff" />
      </div>

      {/* glitch corruption */}
      {glitch > 0 &&
        [...Array(8)].map((_, i) => (
          <div key={i} style={{ position: 'absolute', left: 0, width: '100%', height: 8 + hash(i) * 26, top: `${hash(i + 4) * 100}%`, background: i % 2 ? 'rgba(92,139,255,0.2)' : 'rgba(255,70,70,0.16)', transform: `translateX(${(hash(i + 8) - 0.5) * 220 * glitch}px)`, opacity: glitch }} />
        ))}
      <div className="grain abs-fill" />
    </div>
  );
}
