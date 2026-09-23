import { SceneProps, Bubble, PopWords, Reveal, Sticker, anchorLocal } from './kit';
import { beat, clamp, hash } from '../lib/animationHelpers';

/**
 * SCENE 11 — "Maya's Wisdom"  (split-screen call: chaos vs plants)
 * Chat bubbles with tails, floating emoji reactions, DO NOT SHIP stamp,
 * normal-human vs movie-villain comparison, hangup split.
 */
export function Scene11({ active, local, chunkIdx, wordIdx }: SceneProps & { chunkIdx: number }) {
  if (!active) return <div className="scene-inner" />;
  const aPlants = anchorLocal(11, 'plants');
  const aTwelvek = anchorLocal(11, 'twelvek');
  const aDont = anchorLocal(11, 'dontship');
  const aVillain = anchorLocal(11, 'villain');
  const aHang = anchorLocal(11, 'hangup');
  const end = 35.8;
  const split = clamp((local - (end - 0.8)) / 0.8);

  return (
    <div className="scene-inner">
      {/* split background */}
      <div style={{ position: 'absolute', inset: 0, display: 'flex', transform: `translateX(${-split * 260}px)` }}>
        <div style={{ flex: 1, background: 'linear-gradient(160deg,#31124a,#1a0a2e)', position: 'relative', overflow: 'hidden' }}>
          {/* flying papers */}
          {[...Array(7)].map((_, i) => (
            <div
              key={i}
              style={{
                position: 'absolute', left: `${12 + hash(i) * 70}%`, top: `${8 + hash(i + 5) * 74}%`,
                width: 74 + hash(i + 2) * 60, height: 96 + hash(i + 7) * 50,
                background: 'rgba(240,240,255,0.85)', borderRadius: 6,
                transform: `rotate(${hash(i + 3) * 360}deg)`,
                animation: `floaty ${2.6 + hash(i + 4) * 2}s ease-in-out ${i * 0.3}s infinite`,
                boxShadow: '0 14px 30px rgba(0,0,0,0.35)',
              }}
            >
              <div style={{ margin: '12px 10px', height: 5, background: 'rgba(80,80,120,0.35)', borderRadius: 3 }} />
              <div style={{ margin: '8px 10px', width: '60%', height: 5, background: 'rgba(80,80,120,0.25)', borderRadius: 3 }} />
              <div style={{ margin: '8px 10px', width: '75%', height: 5, background: 'rgba(80,80,120,0.25)', borderRadius: 3 }} />
            </div>
          ))}
          <div style={{ position: 'absolute', left: 44, top: 40, fontFamily: 'var(--font-mono)', fontSize: 15, letterSpacing: '0.3em', color: '#ff8ac2' }}>
            ME · 12K PANIC 📈
          </div>
        </div>
        <div style={{ flex: 1, background: 'linear-gradient(160deg,#0d3b2e,#07281f)', position: 'relative', overflow: 'hidden' }}>
          {[...Array(8)].map((_, i) => (
            <span
              key={i}
              style={{
                position: 'absolute', left: `${8 + hash(i + 10) * 84}%`, top: `${10 + hash(i + 16) * 76}%`,
                fontSize: 40 + hash(i + 11) * 60,
                animation: `sway ${2.2 + hash(i + 12) * 2}s ease-in-out ${i * 0.2}s infinite`,
                transformOrigin: 'bottom center',
                opacity: 0.9,
              }}
            >
              {['🌿', '🪴', '🍃', '🌵'][i % 4]}
            </span>
          ))}
          <div style={{ position: 'absolute', right: 44, top: 40, fontFamily: 'var(--font-mono)', fontSize: 15, letterSpacing: '0.3em', color: '#7dffb0' }}>
            MAYA · PLANTS & WISDOM 🪴
          </div>
        </div>
      </div>

      {/* dialogue bubbles */}
      <div style={{ position: 'absolute', inset: '120px 160px', display: 'flex', flexDirection: 'column', gap: 18 }}>
        <Bubble at={aPlants + 0.3} local={local} side="right" tilt={1.5} bg="rgba(190,255,220,0.96)" width={520} size={22}>
          “If this is about your plants again — talking to them doesn't count as marketing.” 🌱
        </Bubble>
        <Bubble at={aTwelvek - 0.3} local={local} side="left" tilt={-2} bg="rgba(240,225,255,0.96)" width={520} size={22}>
          “Maya. I got a <b style={{ color: '#b3123f' }}>$12,000 order</b>… going to an <b>abandoned warehouse</b>.”
        </Bubble>
        {local > aDont - 1.4 && (
          <div style={{ textAlign: 'center', opacity: beat(local, aDont - 1.4, 0.4) }}>
            <span className="pill" style={{ color: '#5c6a80', background: 'rgba(255,255,255,0.5)', fontSize: 13 }}>…a beat… 🦗</span>
          </div>
        )}
        <Bubble at={aDont - 0.5} local={local} side="right" tilt={-1} bg="rgba(255,214,222,0.97)" width={430} size={24}>
          “Okay. <b style={{ color: '#c3103f' }}>Do NOT ship that.</b>”
        </Bubble>
        {local > aVillain - 2.2 && (
          <div style={{ display: 'flex', gap: 22, justifyContent: 'center', opacity: beat(local, aVillain - 2.2, 0.5) }}>
            <div style={{ background: 'rgba(230,255,240,0.95)', borderRadius: 14, padding: '12px 22px', fontWeight: 700, color: '#0d5c3f', fontSize: 19 }}>🙂 confirm like a normal human</div>
            <div style={{ color: '#8f9bb3', fontSize: 26, alignSelf: 'center' }}>vs</div>
            <div style={{ background: 'rgba(35,10,18,0.9)', border: '2px solid #ff4646', borderRadius: 14, padding: '12px 22px', fontWeight: 700, color: '#ff8fa3', fontSize: 19, transform: 'rotate(-2deg)' }}>😈 like a movie villain</div>
          </div>
        )}
      </div>

      {/* emoji reactions */}
      {local > aTwelvek &&
        ['😱', '🤯', '😂', '🫠'].map((e, i) => (
          <span
            key={i}
            style={{
              position: 'absolute', left: `${34 + i * 12}%`, bottom: 0,
              fontSize: 38, animation: `confetti-fall ${3.4 + i * 0.5}s linear ${aTwelvek * 0 + i * 0.7}s infinite reverse`,
              opacity: 0.9,
            }}
          >
            {e}
          </span>
        ))}

      {/* DO NOT SHIP stamp */}
      {local > aDont + 0.4 && (
        <div
          style={{
            position: 'absolute', right: 120, top: 190,
            transform: `rotate(-12deg) scale(${0.6 + 0.4 * beat(local, aDont + 0.4, 0.4)})`,
            opacity: 0.92,
          }}
        >
          <div style={{ border: '8px solid #ff2b4d', color: '#ff2b4d', fontFamily: 'var(--font-display)', fontSize: 56, padding: '12px 30px', borderRadius: 12, letterSpacing: '0.08em', background: 'rgba(20,2,8,0.35)', boxShadow: '0 0 60px rgba(255,43,77,0.4)', animation: 'pulse-glow 1.4s infinite' }}>
            DO NOT SHIP
          </div>
        </div>
      )}

      <div style={{ position: 'absolute', left: '50%', top: 46, transform: 'translateX(-50%)' }}>
        <PopWords text="I call my friend Maya" at={Math.min(...[aPlants - 4].filter(Number.isFinite))} local={local} size={34} color="#ffd6ec" />
      </div>

      <div style={{ position: 'absolute', left: '50%', bottom: 40, transform: `translateX(-50%) translateX(${split * 120}px)`, width: 1300, background: 'rgba(8,6,16,0.82)', borderRadius: 16, padding: '14px 24px', opacity: 1 - split }}>
        <SyncLineSafe chunkIdx={chunkIdx} wordIdx={wordIdx} />
      </div>
      <div className="grain abs-fill" />
    </div>
  );
}

import { SyncLine } from './kit';
function SyncLineSafe(props: { chunkIdx: number; wordIdx: number }) {
  return <SyncLine {...props} size={31} color="#efe6ff" activeColor="#ff8ac2" />;
}
