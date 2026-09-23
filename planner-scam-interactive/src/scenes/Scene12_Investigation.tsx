import { SceneProps, TypingText, PopWords, Reveal, anchorLocal } from './kit';
import { beat, clamp, hash } from '../lib/animationHelpers';

/**
 * SCENE 12 — "Investigation Montage"  (browser noir, spotlight beams)
 * Three auto-typing searches, fail stamps, jet-ski guy, NOTHING stamp,
 * stomach-drop falling text.
 */
export function Scene12({ active, local, chunkIdx, wordIdx }: SceneProps & { chunkIdx: number }) {
  if (!active) return <div className="scene-inner" />;
  const aDigging = anchorLocal(12, 'digging');
  const aFirst = anchorLocal(12, 'first');
  const aNothing = anchorLocal(12, 'nothing');
  const aSecond = anchorLocal(12, 'second');
  const aJetski = anchorLocal(12, 'jetski');
  const aThird = anchorLocal(12, 'third');
  const aLinked = anchorLocal(12, 'linked');
  const aStomach = anchorLocal(12, 'stomach');
  const aDoor = anchorLocal(12, 'door');
  const end = 28.7;
  const narrow = clamp((local - (end - 1.0)) / 1.0);

  const drop = local > aStomach ? clamp((local - aStomach) / 1.4) : 0;

  return (
    <div className="scene-inner">
      {/* spotlight beams */}
      <div className="abs-fill" style={{ background: '#05060a' }}>
        {[0, 1, 2].map((i) => (
          <div
            key={i}
            style={{
              position: 'absolute', left: `${12 + i * 34}%`, top: '-20%', width: 260, height: '140%',
              background: 'linear-gradient(180deg, rgba(255,215,106,0.13), transparent 80%)',
              transform: `rotate(${(i - 1) * 12}deg)`,
              animation: `sweep-light ${5 + i}s ease-in-out ${i * 0.8}s infinite`,
              filter: 'blur(6px)',
            }}
          />
        ))}
      </div>

      <div style={{ position: 'absolute', left: '50%', top: 44, transform: 'translateX(-50%)' }}>
        <PopWords text="I decide to do a little digging 🕵️" at={aDigging} local={local} size={40} color="#ffd76a" glow="rgba(255,215,106,0.5)" />
      </div>

      {/* three searches */}
      <div style={{ position: 'absolute', left: '50%', top: 150, transform: 'translateX(-50%)', width: 1080, display: 'flex', flexDirection: 'column', gap: 24 }}>
        <SearchRow
          n={1}
          at={aFirst - 0.2}
          query="9 rebar yard industrial edge of town"
          local={local}
          result={local > aNothing ? <Stamp text="NOTHING FOUND" color="#ff4646" /> : null}
        />
        <SearchRow
          n={2}
          at={aSecond - 0.2}
          query={'"elliot graye"'}
          local={local}
          result={
            local > aSecond + 0.6 ? (
              <div style={{ display: 'flex', gap: 14 }}>
                {['🎬 actor', '🦷 dentist', '🛥️ jet-ski guy'].map((r, i) => {
                  const p = beat(local, aSecond + 0.7 + i * 0.5, 0.4);
                  const xAt = local > aJetski + 0.3 + i * 0.12;
                  return (
                    <div key={i} style={{ position: 'relative', background: 'rgba(255,255,255,0.06)', border: '1px solid rgba(255,255,255,0.16)', borderRadius: 12, padding: '10px 18px', fontWeight: 700, color: '#dfe6ff', opacity: p, transform: `scale(${0.8 + 0.2 * p})` }}>
                      {r}
                      <span style={{ position: 'absolute', inset: 0, display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 40, color: '#ff4646', opacity: xAt ? 1 : 0, transform: `rotate(${xAt ? -12 : 20}deg) scale(${xAt ? 1 : 2})`, transition: 'all 0.18s' }}>
                        ❌
                      </span>
                    </div>
                  );
                })}
              </div>
            ) : null
          }
        />
        <SearchRow
          n={3}
          at={aThird - 0.2}
          query="elliot.graye@very-real-buyer.com"
          local={local}
          result={
            local > aLinked ? (
              <div style={{ fontFamily: 'var(--font-mono)', color: '#ff8fa3', fontWeight: 700, fontSize: 19, animation: 'jitter 0.4s linear infinite' }}>
                ⛓ linked to… <span style={{ color: '#fff', fontSize: 24 }}>NOTHING.</span>
              </div>
            ) : null
          }
        />
      </div>

      {/* stomach drop */}
      {drop > 0 && (
        <div
          style={{
            position: 'absolute', left: '50%', top: 60,
            transform: `translateX(-50%) translateY(${drop * 640}px) scale(${1 - drop * 0.2})`,
            opacity: clamp(1.4 - drop),
            fontFamily: 'var(--font-display)', fontSize: 74, color: '#ff5c5c',
            textShadow: '0 14px 44px rgba(255,70,70,0.45)', filter: `blur(${drop * 4}px)`,
          }}
        >
          my stomach drops 📉
        </div>
      )}

      {/* horror flicker */}
      {local > aDoor - 0.4 && (
        <div
          style={{
            position: 'absolute', left: '50%', bottom: 170, transform: 'translateX(-50%)',
            fontFamily: 'var(--font-display)', fontSize: 44, color: '#fff',
            textShadow: '0 0 34px rgba(255,70,70,0.8)',
            opacity: Math.sin(local * 22) > -0.2 ? 1 : 0.15,
            whiteSpace: 'nowrap',
          }}
        >
          “Don't open the door.” 🚪
        </div>
      )}

      <div style={{ position: 'absolute', left: '50%', bottom: 56, transform: 'translateX(-50%)', width: 1300, background: 'rgba(4,5,9,0.82)', borderRadius: 16, padding: '14px 24px', border: '1px solid rgba(255,215,106,0.2)' }}>
        <SyncLineC chunkIdx={chunkIdx} wordIdx={wordIdx} />
      </div>
      <div className="grain abs-fill" />
      {/* spotlight narrowing */}
      <div className="abs-fill" style={{ background: 'radial-gradient(46% 60% at 50% 46%, transparent 40%, #05060a 100%)', opacity: narrow, transition: 'opacity 0.3s' }} />
    </div>
  );
}

import { SyncLine } from './kit';
function SyncLineC(props: { chunkIdx: number; wordIdx: number }) {
  return <SyncLine {...props} size={30} color="#e8ecff" activeColor="#ffd76a" />;
}

function SearchRow({ n, at, query, local, result }: { n: number; at: number; query: string; local: number; result: React.ReactNode }) {
  const p = beat(local, at, 0.4);
  return (
    <div style={{ opacity: p, transform: `translateY(${(1 - p) * 30}px)` }}>
      <div className="card" style={{ padding: '16px 22px', display: 'flex', alignItems: 'center', gap: 16, background: 'rgba(10,12,18,0.8)' }}>
        <span style={{ fontFamily: 'var(--font-display)', color: '#ffd76a', fontSize: 22 }}>{n}.</span>
        <span style={{ fontSize: 22 }}>🔍</span>
        <div style={{ flex: 1, fontFamily: 'var(--font-mono)', fontSize: 19, color: '#dfe6ff' }}>
          <TypingText text={query} at={at + 0.2} dur={0.9} local={local} caret={false} />
        </div>
      </div>
      {result && <div style={{ marginTop: 10, marginLeft: 66 }}>{result}</div>}
    </div>
  );
}

function Stamp({ text, color }: { text: string; color: string }) {
  return (
    <span
      style={{
        display: 'inline-block', border: `4px solid ${color}`, color,
        fontFamily: 'var(--font-display)', fontSize: 24, letterSpacing: '0.12em',
        padding: '6px 18px', borderRadius: 8, transform: 'rotate(-6deg)',
        background: 'rgba(30,4,8,0.5)', boxShadow: `0 0 30px ${color}55`,
      }}
    >
      {text}
    </span>
  );
}

function NothingStamp() {
  return null;
}
void NothingStamp; void hash;
