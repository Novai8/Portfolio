import { SceneProps, SyncLine, PopChars, Reveal, anchorLocal } from './kit';
import { beat, clamp } from '../lib/animationHelpers';

/**
 * SCENE 04 — "THE BIG REVEAL"  (explosive comic-book)
 * Speed lines, order card slam, 500 spin-up, $12,480 with dollar rain,
 * screen shake, chromatic "FIVE... HUNDRED?!", kaleidoscope out.
 */
export function Scene04({ active, local, chunkIdx, wordIdx }: SceneProps & { chunkIdx: number }) {
  if (!active) return <div className="scene-inner" />;
  const aUpdates = anchorLocal(4, 'updates');
  const aSingle = anchorLocal(4, 'single');
  const a500 = anchorLocal(4, 'fivehundred');
  const aTotal = anchorLocal(4, 'total');
  const aWhisper = anchorLocal(4, 'whisper');
  const end = 22.5;
  const out = clamp((local - (end - 1.0)) / 1.0);

  const shake = local > aSingle + 0.15 && local < aSingle + 1.0 ? 1 : 0;

  return (
    <div className="scene-inner">
      {/* radial manga speed lines */}
      <div
        className="abs-fill"
        style={{
          background:
            'repeating-conic-gradient(from 0deg at 50% 46%, rgba(255,255,255,0.075) 0deg 3deg, transparent 3deg 11deg)',
          animation: `spin-slow ${14}s linear infinite`,
          transform: `scale(${1 + out * 0.7})`,
          maskImage: 'radial-gradient(circle at 50% 46%, transparent 0 6%, #000 45%)',
        }}
      />
      {/* comic halo */}
      <div
        className="layer"
        style={{
          left: '50%', top: '44%', width: 560, height: 560, margin: '-280px 0 0 -280px', borderRadius: '50%',
          background: 'radial-gradient(circle, rgba(255,0,110,0.22), transparent 65%)',
          animation: 'breathe 2.2s ease-in-out infinite',
        }}
      />

      <div style={{ position: 'absolute', left: '50%', top: 46, transform: 'translateX(-50%)' }}>
        <PopChars text="THEN MY SCREEN UPDATES." at={aUpdates} local={local} size={40} color="#fff" glow="0 0 24px rgba(255,0,110,0.8)" stagger={0.028} />
      </div>

      {/* the order card */}
      <div
        className={shake ? 'shake-hard' : undefined}
        style={{
          position: 'absolute', left: '50%', top: '47%',
          transform: `translate(-50%,-50%) perspective(1100px) rotateX(${8 - out * 6}deg) scale(${1 + out * 2.2})`,
        }}
      >
        <div
          style={{
            width: 760, borderRadius: 30, padding: '40px 56px',
            background: 'linear-gradient(135deg,#7c3aed 0%, #ff006e 100%)',
            boxShadow: '0 60px 140px rgba(255,0,110,0.35), inset 0 0 0 4px rgba(255,255,255,0.14)',
            textAlign: 'center',
            transform: `translateY(${(1 - beat(local, aSingle - 0.35, 0.45)) * -520}px) rotateX(${(1 - beat(local, aSingle - 0.35, 0.45)) * 70}deg)`,
            opacity: beat(local, aSingle - 0.35, 0.3),
          }}
        >
          <div style={{ fontFamily: 'var(--font-mono)', letterSpacing: '0.3em', color: 'rgba(255,255,255,0.75)', fontSize: 17 }}>
            NEW ORDER · UNEXPECTED
          </div>
          <div style={{ margin: '10px 0 2px' }}>
            <span
              style={{
                fontFamily: 'var(--font-display)', fontSize: 168, color: '#fff', lineHeight: 1,
                textShadow: '0 0 60px rgba(255,255,255,0.45)',
                display: 'inline-block',
              }}
            >
              <SpinNumber target={500} at={a500} dur={1.4} local={local} />
            </span>
          </div>
          <div style={{ fontFamily: 'var(--font-display)', fontSize: 30, letterSpacing: '0.28em', color: '#ffd6e9' }}>PLANNERS</div>
          <div
            style={{
              marginTop: 18, fontFamily: 'var(--font-display)', fontSize: 84, color: '#00ff88',
              textShadow: '0 0 40px rgba(0,255,136,0.6)',
              transform: `scale(${0.4 + 0.6 * beat(local, aTotal, 0.5)}) rotate(${(1 - beat(local, aTotal, 0.5)) * -8}deg)`,
              opacity: beat(local, aTotal - 0.1, 0.2),
            }}
          >
            $12,480
          </div>
        </div>
      </div>

      {/* dollar rain */}
      {local > aTotal &&
        [...Array(18)].map((_, i) => (
          <span
            key={i}
            style={{
              position: 'absolute', left: `${3 + i * 5.3}%`, top: -60,
              fontSize: 26 + (i % 4) * 12, color: '#7dffa8', fontWeight: 900,
              animation: `rain-dollar ${2.2 + (i % 5) * 0.5}s linear ${(i * 0.22).toFixed(2)}s infinite`,
              opacity: 0,
            }}
          >
            $
          </span>
        ))}

      {/* impact stars */}
      {local > aSingle &&
        [...Array(10)].map((_, i) => {
          const ang = (i / 10) * Math.PI * 2 + local * 0.4;
          const rad = 300 + Math.sin(local * 2 + i) * 60;
          return (
            <span
              key={i}
              style={{
                position: 'absolute', left: `calc(50% + ${Math.cos(ang) * rad}px)`, top: `calc(46% + ${Math.sin(ang) * rad * 0.72}px)`,
                fontSize: 30 + (i % 3) * 14, color: '#ffd35c',
                textShadow: '0 0 20px rgba(255,211,92,0.8)',
                transform: `rotate(${local * 120 + i * 36}deg) scale(${0.7 + 0.3 * Math.sin(local * 3 + i)})`,
                opacity: 0.85,
              }}
            >
              ✦
            </span>
          );
        })}

      {/* comic burst text */}
      {local > aWhisper - 0.4 && (
        <div style={{ position: 'absolute', left: '50%', bottom: 96, transform: 'translateX(-50%)', textAlign: 'center' }}>
          <div
            style={{
              transform: `rotate(-3deg) scale(${1 + 0.2 * Math.sin(local * 6)})`,
            }}
          >
            <span style={{ fontFamily: 'var(--font-display)', fontSize: 92, color: '#ff006e', textShadow: '5px 5px 0 #00e5ff, -5px -5px 0 #7c3aed, 0 0 46px rgba(255,0,110,0.6)', letterSpacing: '0.02em' }}>
              “FIVE… HUNDRED?!”
            </span>
          </div>
        </div>
      )}

      {/* narration strip */}
      <div
        style={{
          position: 'absolute', left: '50%', top: 130, transform: 'translateX(-50%)', width: 1200,
          opacity: local < aSingle - 0.2 ? 1 : 0, transition: 'opacity 0.3s',
        }}
      >
        <SyncLine chunkIdx={chunkIdx} wordIdx={wordIdx} size={34} color="#ffd6e9" activeColor="#fff" />
      </div>
      <div className="grain abs-fill" />
    </div>
  );
}

function SpinNumber({ target, at, dur, local }: { target: number; at: number; dur: number; local: number }) {
  const p = beat(local, at, dur);
  const eased = 1 - Math.pow(1 - p, 3);
  const val = Math.round(target * eased);
  return (
    <span style={{ filter: p > 0 && p < 1 ? 'blur(2.4px)' : undefined, display: 'inline-block' }}>
      {val}
    </span>
  );
}
