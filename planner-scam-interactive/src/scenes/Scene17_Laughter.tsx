import { SceneProps, SyncLine, PopWords, Reveal, Sticker, Floaty, anchorLocal } from './kit';
import { beat, clamp, hash } from '../lib/animationHelpers';

/**
 * SCENE 17 — "Laughter & Realization"  (confetti celebration)
 * Real laughing, HA-HA-HA bounce, expectation-vs-reality split,
 * sunrise time-lapse, cautious legit email.
 */
export function Scene17({ active, local, chunkIdx, wordIdx }: SceneProps & { chunkIdx: number }) {
  if (!active) return <div className="scene-inner" />;
  const aLaugh = anchorLocal(17, 'laughing');
  const aColors = anchorLocal(17, 'colors');
  const aGoblin = anchorLocal(17, 'goblin');
  const aMorning = anchorLocal(17, 'morning');
  const aLegit = anchorLocal(17, 'legit');
  const aTwitch = anchorLocal(17, 'twitch');
  const end = 49.4;
  const wipe = clamp((local - (end - 1.0)) / 1.0);

  return (
    <div className="scene-inner">
      {/* confetti */}
      {[...Array(26)].map((_, i) => (
        <span
          key={i}
          style={{
            position: 'absolute', left: `${hash(i) * 100}%`, top: -40,
            width: 10 + hash(i + 2) * 8, height: 14 + hash(i + 4) * 10,
            background: ['#ff5c8a', '#ffd35c', '#7dd8a8', '#9fc6ff', '#c9a3ff'][i % 5],
            borderRadius: 3,
            animation: `confetti-fall ${3.4 + hash(i + 6) * 2.6}s linear ${hash(i + 8) * 3}s infinite`,
            opacity: 0.85,
            ['--drift' as string]: `${(hash(i + 10) - 0.5) * 160}px`,
          }}
        />
      ))}

      {/* relaxed hands on keyboard */}
      <Floaty size={110} x={120} y={430} period={3.6}>🧘‍♀️</Floaty>
      <Floaty size={90} x={210} y={560} period={4.2} delay={0.5}>💻</Floaty>

      {/* HA HA HA bounce */}
      {local > aLaugh - 0.2 && (
        <div style={{ position: 'absolute', left: 430, top: 110, display: 'flex', gap: 8 }}>
          {'HA HA HA'.split('').map((ch, i) => (
            <span
              key={i}
              style={{
                fontFamily: 'var(--font-display)', fontSize: ch === ' ' ? 24 : 58 + (i % 3) * 14,
                color: ['#ffd35c', '#ff5c8a', '#7dd8a8'][i % 3],
                display: 'inline-block', whiteSpace: 'pre',
                animation: `bounce-letter ${1.1 + (i % 3) * 0.16}s ease-in-out ${i * 0.09}s infinite`,
                textShadow: '0 8px 30px rgba(255,211,92,0.35)',
                opacity: beat(local, aLaugh - 0.2 + i * 0.06, 0.3),
              }}
            >
              {ch}
            </span>
          ))}
        </div>
      )}

      {/* expectation vs reality */}
      <Reveal at={aColors - 0.6} local={local} rise={34} style={{ position: 'absolute', left: '50%', top: 250, transform: 'translateX(-50%)' }}>
        <div style={{ display: 'flex', gap: 40 }}>
          <div className="card" style={{ width: 520, padding: '26px 32px', background: 'rgba(255,240,250,0.92)', transform: 'rotate(-1.6deg)', borderColor: 'rgba(255,92,138,0.4)' }}>
            <div style={{ fontFamily: 'var(--font-mono)', fontSize: 12.5, letterSpacing: '0.3em', color: '#c2497c', marginBottom: 12 }}>
              EXPECTATION · WHAT I THOUGHT
            </div>
            <div style={{ display: 'flex', gap: 12, flexWrap: 'wrap' }}>
              {['🎨 brand colors', '✨ motivational quotes', '📱 posting consistently', '☕ aesthetic cafe'].map((t, i) => (
                <span key={i} style={{ background: '#ffe3ef', borderRadius: 999, padding: '8px 16px', fontWeight: 700, color: '#8f2d5c', fontSize: 17.5, opacity: beat(local, aColors + i * 0.3, 0.4), animation: 'floaty-soft 3s ease-in-out infinite' }}>
                  {t}
                </span>
              ))}
            </div>
          </div>
          <div className="card" style={{ width: 520, padding: '26px 32px', background: 'rgba(16,4,20,0.88)', transform: 'rotate(1.8deg)', borderColor: 'rgba(143,123,255,0.5)', boxShadow: '0 30px 80px rgba(143,123,255,0.25)' }}>
            <div style={{ fontFamily: 'var(--font-mono)', fontSize: 12.5, letterSpacing: '0.3em', color: '#c9a3ff', marginBottom: 12 }}>
              REALITY · 2:00 A.M.
            </div>
            <div style={{ display: 'flex', gap: 12, flexWrap: 'wrap' }}>
              {['👹 cyber-goblin wrestling', '🩳 pajama pants', '🧠 fraud bootcamp', '🦝 raccoon landlords'].map((t, i) => {
                const p = beat(local, aGoblin - 0.2 + i * 0.34, 0.4);
                return (
                  <span key={i} style={{ background: 'rgba(143,123,255,0.16)', border: '1.5px solid rgba(201,163,255,0.5)', borderRadius: 999, padding: '8px 16px', fontWeight: 700, color: '#e6ddff', fontSize: 17.5, opacity: p, transform: `rotate(${(hash(i) - 0.5) * 8}deg) scale(${0.8 + 0.2 * p})`, animation: 'jitter 0.6s steps(2) infinite' }}>
                    {t}
                  </span>
                );
              })}
            </div>
          </div>
        </div>
      </Reveal>

      {/* sunrise time-lapse */}
      {local > aMorning - 0.8 && (
        <div style={{ position: 'absolute', left: '50%', bottom: 150, transform: 'translateX(-50%)', textAlign: 'center' }}>
          <div
            style={{
              width: 130, height: 130, borderRadius: '50%',
              background: 'radial-gradient(circle at 40% 35%, #fff3c4, #ffb347 70%, #ff9a3c)',
              boxShadow: '0 0 90px rgba(255,179,71,0.8)',
              animation: `sunrise-rise ${3.4}s ease-in-out infinite alternate`,
            }}
          />
          <div style={{ fontFamily: 'var(--font-hand)', fontSize: 30, color: '#ffd98a', marginTop: 8 }}>
            the next morning 🌅
          </div>
        </div>
      )}

      {/* cautious email */}
      {local > aLegit - 1.2 && (() => {
        const p = beat(local, aLegit - 1.2, 0.5);
        const tremble = local < aLegit + 3 ? 1 : 0;
        return (
          <div
            style={{
              position: 'absolute', right: 120, bottom: 250,
              transform: `translateX(${(1 - p) * 320}px) rotate(${tremble ? Math.sin(local * 18) * 1.6 : 0}deg)`,
              opacity: p,
            }}
          >
            <div className="card" style={{ width: 470, padding: '20px 28px', background: 'rgba(255,255,255,0.94)', color: '#23262e' }}>
              <div style={{ fontFamily: 'var(--font-mono)', fontSize: 13, color: '#7f8cab' }}>📩 new email · subject:</div>
              <div style={{ fontFamily: 'var(--font-display)', fontSize: 26, marginTop: 6 }}>
                “Order Inquiry (<span style={{ color: '#0e9f6e' }}>Legit</span>)” 🤨
              </div>
              <div style={{ fontFamily: 'var(--font-hand)', fontSize: 25, color: '#5b6478', marginTop: 6 }}>
                “Hi! I run a coworking space… can we talk?”
              </div>
            </div>
          </div>
        );
      })()}

      {local > aTwitch - 0.2 && (
        <div style={{ position: 'absolute', left: 170, bottom: 220, transform: `rotate(${Math.sin(local * 26) * 2}deg)`, opacity: beat(local, aTwitch - 0.2, 0.3) }}>
          <div style={{ fontSize: 64 }}>👁️</div>
          <div style={{ fontFamily: 'var(--font-hand)', fontSize: 27, color: '#ffb3c8' }}>my eye twitches</div>
        </div>
      )}

      <div style={{ position: 'absolute', left: '50%', top: 56, transform: 'translateX(-50%)' }}>
        <PopWords text="I start laughing — real laughing" at={aLaugh} local={local} size={40} color="#ffe9b3" glow="rgba(255,211,92,0.5)" />
      </div>

      <div style={{ position: 'absolute', left: '50%', bottom: 48, transform: 'translateX(-50%)', width: 1320, background: 'rgba(14,10,26,0.8)', borderRadius: 16, padding: '14px 24px', border: '1px solid rgba(255,211,92,0.25)', opacity: 1 - wipe * 0.6 }}>
        <SyncLine chunkIdx={chunkIdx} wordIdx={wordIdx} size={30} color="#fff3d6" activeColor="#ffd35c" />
      </div>

      {/* sun circular wipe OUT */}
      <div
        className="abs-fill"
        style={{
          background: 'radial-gradient(circle at 50% 62%, #fff7e0 0 30%, #ffca6a 45%, rgba(255,150,60,0.9) 70%)',
          clipPath: `circle(${wipe * 120}% at 50% 62%)`,
        }}
      />
      <div className="grain abs-fill" />
    </div>
  );
}
