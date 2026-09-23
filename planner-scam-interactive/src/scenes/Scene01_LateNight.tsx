import { SceneProps, SyncLine, PopWords, Sticker, Floaty, Reveal, anchorLocal } from './kit';

/**
 * SCENE 01 — "Late Night Launch"  (paper-cutout collage, midnight gradient)
 * 2:07 a.m. clock, laptop on a laundry basket, cereal mug particle pour,
 * ENTREPRENEUR NOW badge spring-in. Everything wobbles. Nothing sleeps.
 */
export function Scene01({ active, local, chunkIdx, wordIdx }: SceneProps & { chunkIdx: number }) {
  if (!active) return <div className="scene-inner" />;
  const aLaptop = anchorLocal(1, 'laptop');
  const aCereal = anchorLocal(1, 'cereal');
  const aEntr = anchorLocal(1, 'entrepreneur');
  const end = 12.11;
  const out = Math.max(0, (local - (end - 0.8)) / 0.8); // whoosh zoom out

  return (
    <div className="scene-inner" style={{ transform: `scale(${1 + out * 1.6})`, filter: `brightness(${1 - out * 0.6})` }}>
      {/* paper-cutout clouds/shapes */}
      <div className="layer" style={{ left: -60, top: 70, width: 340, height: 130, background: 'rgba(255,255,255,0.06)', borderRadius: 90, animation: 'drift-x 9s ease-in-out infinite' }} />
      <div className="layer" style={{ right: -40, top: 160, width: 420, height: 150, background: 'rgba(143,123,255,0.10)', borderRadius: 100, animation: 'drift-x 11s ease-in-out infinite reverse' }} />
      <div className="layer" style={{ left: 120, bottom: 220, width: 260, height: 110, background: 'rgba(0,194,255,0.07)', borderRadius: 80, animation: 'floaty 8s ease-in-out infinite' }} />

      {/* animated clock — 2:07, glowing pulse */}
      <Reveal at={0.4} local={local} rise={30} style={{ position: 'absolute', left: 120, top: 90 }}>
        <div style={{ position: 'relative', width: 190, height: 190, animation: 'pulse-glow 1.6s ease-in-out infinite', color: '#8f7bff' }}>
          <svg width="190" height="190" viewBox="0 0 190 190">
            <circle cx="95" cy="95" r="86" fill="rgba(10,12,34,0.85)" stroke="#8f7bff" strokeWidth="7" />
            <circle cx="95" cy="95" r="86" fill="none" stroke="rgba(255,255,255,0.12)" strokeWidth="2" strokeDasharray="4 10" style={{ animation: 'spin-slow 24s linear infinite', transformOrigin: '95px 95px' }} />
            {/* hour hand → 2 */}
            <line x1="95" y1="95" x2="95" y2="48" stroke="#fff" strokeWidth="9" strokeLinecap="round" transform="rotate(60 95 95)" />
            {/* minute hand → ~07 */}
            <line x1="95" y1="95" x2="95" y2="30" stroke="#00ff88" strokeWidth="6" strokeLinecap="round" transform="rotate(42 95 95)" />
            <circle cx="95" cy="95" r="9" fill="#00ff88" />
          </svg>
          <div style={{ position: 'absolute', width: '100%', textAlign: 'center', top: 200, fontFamily: 'var(--font-mono)', color: '#b9a8ff', fontSize: 26, fontWeight: 700, letterSpacing: '0.2em', opacity: local > 1 ? 1 : 0, transition: 'opacity 0.4s' }}>
            2:07 A.M.
          </div>
        </div>
      </Reveal>

      {/* laptop balanced on laundry basket */}
      <Reveal at={aLaptop - 0.6} local={local} rise={46} style={{ position: 'absolute', left: 470, bottom: 120, transformOrigin: 'bottom center' }}>
        <div style={{ textAlign: 'center', transformOrigin: 'bottom center', animation: 'wobble 2.4s ease-in-out infinite' }}>
          <div style={{ fontSize: 120, lineHeight: 0.9, filter: 'drop-shadow(0 0 34px rgba(0,194,255,0.5))' }}>💻</div>
          <div style={{ fontSize: 110, lineHeight: 0.72 }}>🧺</div>
          <div style={{ fontFamily: 'var(--font-hand)', color: '#9fe8ff', fontSize: 30, marginTop: 10, transform: 'rotate(-3deg)' }}>
            office = laundry basket
          </div>
        </div>
      </Reveal>

      {/* cereal mug with particle pour */}
      <Reveal at={aCereal - 0.5} local={local} rise={40} style={{ position: 'absolute', right: 150, bottom: 150 }}>
        <div style={{ position: 'relative', animation: 'floaty-soft 3s ease-in-out infinite' }}>
          {/* pour particles */}
          {[...Array(9)].map((_, i) => (
            <span
              key={i}
              style={{
                position: 'absolute', top: -46, left: 34 + (i % 3) * 12,
                width: 9, height: 9, borderRadius: '50%',
                background: ['#ffd35c', '#ff9a3c', '#fff5c0'][i % 3],
                animation: `drip ${0.7 + (i % 4) * 0.16}s linear ${i * 0.12}s infinite`,
              }}
            />
          ))}
          <div style={{ fontSize: 120 }}>🥣</div>
          <div style={{ fontFamily: 'var(--font-hand)', color: '#ffd35c', fontSize: 30, transform: 'rotate(2deg)', marginTop: 6 }}>
            coffee mug cereal™
          </div>
        </div>
      </Reveal>

      {/* floating story emoji */}
      <Floaty size={54} x={260} y={330} period={4} opacity={0.9}>🌙</Floaty>
      <Floaty size={44} x={1320} y={260} period={5} delay={0.6} opacity={0.8}>✨</Floaty>
      <Floaty size={40} x={820} y={120} period={3.4} delay={1.1} opacity={0.7}>💤</Floaty>

      {/* big badge */}
      <div style={{ position: 'absolute', left: '50%', top: 96, transform: 'translateX(-50%)' }}>
        <Sticker at={aEntr - 0.5} local={local} tilt={-4} bg="linear-gradient(135deg,#00ff88,#00c2ff)" color="#04120c" size={34} pad="16px 30px">
          ENTREPRENEUR NOW
        </Sticker>
      </div>

      {/* narration */}
      <div style={{ position: 'absolute', left: '50%', top: 470, transform: 'translateX(-50%)', width: 1240 }}>
        <PopWords
          text="I need you to imagine this:"
          at={0.05}
          local={local}
          size={52}
          color="#ffffff"
          glow="rgba(143,123,255,0.6)"
        />
      </div>
      <div style={{ position: 'absolute', left: '50%', bottom: 150, transform: 'translateX(-50%)', width: 1300 }}>
        <SyncLine chunkIdx={chunkIdx} wordIdx={wordIdx} size={40} color="#e8ecff" activeColor="#00ff88" />
      </div>

      {/* paper grain */}
      <div className="grain abs-fill" />
    </div>
  );
}
