import { CSSProperties, ReactNode } from 'react';
import { WORDS, CHUNKS, SCENES } from '../lib/audioSync';
import ANCHORS from '../data/anchors.json';
import { beat, clamp, hash } from '../lib/animationHelpers';

export type Anchors = Record<string, number>;
export const ALL_ANCHORS = ANCHORS as Record<string, Anchors>;

/** Scene-local time for a scene id + anchor key. */
export function anchorLocal(sceneId: number, key: string): number {
  const a = ALL_ANCHORS[String(sceneId)]?.[key];
  const s = SCENES[sceneId - 1];
  return a !== undefined && s ? a - s.start : Number.POSITIVE_INFINITY;
}

export interface SceneProps {
  active: boolean;
  /** seconds since this scene began */
  local: number;
  /** global audio time */
  g: number;
  wordIdx: number;
}

// ---------------------------------------------------------------------------
// Kinetic word-line synced to the real word timestamps of the current chunk.
// Every word enters exactly when it is spoken; spoken words solidify, the
// active word pops, upcoming words stay ghosted.
// ---------------------------------------------------------------------------
export function SyncLine({
  chunkIdx,
  wordIdx,
  style,
  size = 44,
  color = '#ffffff',
  activeColor = '#00ff88',
  align = 'center',
  ghostOpacity = 0.22,
  weight = 900,
}: {
  chunkIdx: number;
  wordIdx: number;
  style?: CSSProperties;
  size?: number | string;
  color?: string;
  activeColor?: string;
  align?: CSSProperties['textAlign'];
  ghostOpacity?: number;
  weight?: number;
}) {
  const chunk = CHUNKS[chunkIdx];
  if (!chunk) return null;
  return (
    <div style={{ textAlign: align, ...style }}>
      {WORDS.slice(chunk.w0, chunk.w1 + 1).map((w, i) => {
        const gi = chunk.w0 + i;
        const isSpoken = gi < wordIdx;
        const isActive = gi === wordIdx;
        const scale = isActive ? 1.14 : isSpoken ? 1.02 : 0.94;
        return (
          <span
            key={gi}
            className="kinetic-word"
            style={{
              fontSize: size,
              fontWeight: weight,
              fontFamily: 'var(--font-display)',
              color: isActive ? activeColor : color,
              opacity: isActive ? 1 : isSpoken ? 0.92 : ghostOpacity,
              transform: `scale(${scale}) translateY(${isActive ? -5 : 0}px)`,
              textShadow: isActive ? `0 0 26px ${activeColor}88` : 'none',
              transition: 'transform 90ms linear',
              margin: '0 0.16em',
            }}
          >
            {w.word}
          </span>
        );
      })}
    </div>
  );
}

// ---------------------------------------------------------------------------
// Phrase that pops in word-by-word at a chosen local time (decorative lines).
// ---------------------------------------------------------------------------
export function PopWords({
  text,
  at,
  local,
  stagger = 0.07,
  dur = 0.5,
  size = 30,
  color = '#fff',
  font = 'var(--font-display)',
  weight = 900,
  glow,
  rise = 34,
  opacityTarget = 1,
}: {
  text: string;
  at: number;
  local: number;
  stagger?: number;
  dur?: number;
  size?: number | string;
  color?: string;
  font?: string;
  weight?: number;
  glow?: string;
  rise?: number;
  opacityTarget?: number;
}) {
  const words = text.split(' ');
  return (
    <div style={{ textAlign: 'center' }}>
      {words.map((w, i) => {
        const p = beat(local, at + i * stagger, dur);
        const back = 1 + 2.2 * Math.pow(1 - p, 2) * p; // overshoot-ish
        return (
          <span
            key={i}
            className="kinetic-word"
            style={{
              fontSize: size,
              fontWeight: weight,
              fontFamily: font,
              color,
              opacity: p * opacityTarget,
              transform: `translateY(${(1 - p) * rise}px) scale(${0.6 + 0.4 * back}) rotate(${(hash(i + text.length) - 0.5) * 6 * (1 - p)}deg)`,
              textShadow: glow ? `0 0 22px ${glow}` : undefined,
              margin: '0 0.14em',
            }}
          >
            {w}
          </span>
        );
      })}
    </div>
  );
}

/** Letters of a word/phrase pop individually (comic-book moments). */
export function PopChars({
  text,
  at,
  local,
  stagger = 0.04,
  size = 60,
  color = '#fff',
  spin = 180,
  font = 'var(--font-display)',
  glow,
}: {
  text: string;
  at: number;
  local: number;
  stagger?: number;
  size?: number | string;
  color?: string;
  spin?: number;
  font?: string;
  glow?: string;
}) {
  return (
    <div style={{ textAlign: 'center' }}>
      {text.split('').map((ch, i) => {
        const p = beat(local, at + i * stagger, 0.45);
        return (
          <span
            key={i}
            className="char"
            style={{
              fontSize: size,
              fontFamily: font,
              color,
              opacity: p,
              transform: `rotate(${(1 - p) * spin}deg) scale(${0.2 + 0.8 * p})`,
              textShadow: glow,
              display: 'inline-block',
              whiteSpace: 'pre',
            }}
          >
            {ch}
          </span>
        );
      })}
    </div>
  );
}

/** Auto-typing text with blinking caret (types over `dur` seconds from `at`). */
export function TypingText({
  text,
  at,
  dur,
  local,
  size = 18,
  color = '#dfe6ff',
  font = 'var(--font-mono)',
  caret = true,
  opacityAt = 1,
}: {
  text: string;
  at: number;
  dur: number;
  local: number;
  size?: number | string;
  color?: string;
  font?: string;
  caret?: boolean;
  opacityAt?: number;
}) {
  const p = beat(local, at, dur);
  const n = Math.floor(p * text.length);
  const done = p >= 1;
  return (
    <span style={{ fontSize: size, color, fontFamily: font, opacity: opacityAt }}>
      {text.slice(0, n)}
      {caret && (
        <span style={{ opacity: done ? 0 : 1, animation: done ? undefined : 'blink-caret 0.8s step-end infinite' }}>
          ▌
        </span>
      )}
    </span>
  );
}

/** Number that counts up from 0→target between at..at+dur. */
export function Counter({
  target,
  at,
  dur,
  local,
  prefix = '',
  suffix = '',
  size = 64,
  color = '#fff',
  font = 'var(--font-display)',
  blurWhileRolling = true,
}: {
  target: number;
  at: number;
  dur: number;
  local: number;
  prefix?: string;
  suffix?: string;
  size?: number | string;
  color?: string;
  font?: string;
  blurWhileRolling?: boolean;
}) {
  const p = beat(local, at, dur);
  const eased = 1 - Math.pow(1 - p, 3);
  const val = Math.round(target * eased);
  return (
    <span
      style={{
        fontSize: size,
        color,
        fontFamily: font,
        display: 'inline-block',
        filter: blurWhileRolling && p > 0 && p < 1 ? 'blur(1.6px)' : undefined,
        transform: `scale(${1 + 0.12 * Math.sin(Math.PI * p)})`,
      }}
    >
      {prefix}
      {val.toLocaleString('en-US')}
      {suffix}
    </span>
  );
}

/** Checklist row with animated check. */
export function CheckRow({
  label,
  at,
  local,
  done = '✅',
  pending = '⬜',
  size = 22,
  color = '#eafff5',
  strike = false,
}: {
  label: string;
  at: number;
  local: number;
  done?: string;
  pending?: string;
  size?: number | string;
  color?: string;
  strike?: boolean;
}) {
  const p = beat(local, at, 0.35);
  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: 12, transform: `translateX(${(1 - p) * -30}px)`, opacity: 0.25 + 0.75 * p }}>
      <span style={{ fontSize: size, transform: `scale(${1 + 0.6 * p * (1 - p) * 4})`, display: 'inline-block' }}>
        {p >= 1 ? done : pending}
      </span>
      <span style={{ fontSize: size, fontWeight: 700, color, textDecoration: strike && p >= 1 ? 'line-through' : undefined, opacity: p >= 1 ? 1 : 0.7 }}>
        {label}
      </span>
    </div>
  );
}

/** Speech bubble with tail; pops in at `at`. */
export function Bubble({
  children,
  at,
  local,
  side = 'left',
  bg = 'rgba(255,255,255,0.94)',
  color = '#101426',
  width = 380,
  tilt = 0,
  size = 19,
}: {
  children: ReactNode;
  at: number;
  local: number;
  side?: 'left' | 'right';
  bg?: string;
  color?: string;
  width?: number | string;
  tilt?: number;
  size?: number;
}) {
  const p = beat(local, at, 0.4);
  return (
    <div
      style={{
        position: 'relative',
        width,
        background: bg,
        color,
        borderRadius: 18,
        padding: '16px 20px',
        fontSize: size,
        fontWeight: 700,
        lineHeight: 1.4,
        boxShadow: '0 18px 44px rgba(0,0,0,0.4)',
        transform: `scale(${0.5 + 0.5 * p}) translateY(${(1 - p) * 26}px) rotate(${tilt * p}deg)`,
        opacity: clamp(p * 1.4),
        transformOrigin: side === 'left' ? 'left bottom' : 'right bottom',
        alignSelf: side === 'left' ? 'flex-start' : 'flex-end',
      }}
    >
      {children}
      <div
        style={{
          position: 'absolute',
          bottom: -12,
          [side]: 34,
          width: 0,
          height: 0,
          borderLeft: '12px solid transparent',
          borderRight: '12px solid transparent',
          borderTop: `14px solid ${bg}`,
        } as CSSProperties}
      />
    </div>
  );
}

/** Rotated sticker / badge. */
export function Sticker({
  children,
  at,
  local,
  tilt = -6,
  bg = '#ffe14d',
  color = '#181000',
  size = 20,
  pad = '12px 20px',
}: {
  children: ReactNode;
  at: number;
  local: number;
  tilt?: number;
  bg?: string;
  color?: string;
  size?: number;
  pad?: string;
}) {
  const p = beat(local, at, 0.5);
  return (
    <div
      style={{
        display: 'inline-block',
        background: bg,
        color,
        fontWeight: 900,
        fontSize: size,
        padding: pad,
        borderRadius: 12,
        transform: `rotate(${tilt}deg) scale(${0.3 + 0.7 * p})`,
        opacity: p,
        boxShadow: '0 12px 30px rgba(0,0,0,0.45), inset 0 0 0 3px rgba(0,0,0,0.12)',
        fontFamily: 'var(--font-display)',
        letterSpacing: '0.02em',
      }}
    >
      {children}
    </div>
  );
}

/** Horizontal meter that fills from at..at+dur. */
export function Meter({
  at,
  dur,
  local,
  color = '#ff3b5c',
  height = 12,
  width = 260,
  track = 'rgba(255,255,255,0.12)',
}: {
  at: number; dur: number; local: number; color?: string; height?: number; width?: number; track?: string;
}) {
  const p = beat(local, at, dur);
  return (
    <div style={{ width, height, borderRadius: height, background: track, overflow: 'hidden' }}>
      <div style={{ width: `${p * 100}%`, height: '100%', background: color, borderRadius: height, boxShadow: `0 0 14px ${color}` }} />
    </div>
  );
}

/** Floating emoji/icon with infinite bob. */
export function Floaty({
  children,
  size = 64,
  x = 0,
  y = 0,
  period = 3,
  delay = 0,
  opacity = 1,
  anim = 'floaty',
}: {
  children: ReactNode;
  size?: number | string;
  x?: number | string;
  y?: number | string;
  period?: number;
  delay?: number;
  opacity?: number;
  anim?: string;
}) {
  return (
    <div
      style={{
        position: 'absolute',
        left: x,
        top: y,
        fontSize: size,
        lineHeight: 1,
        opacity,
        animation: `${anim} ${period}s ease-in-out ${delay}s infinite`,
        filter: 'drop-shadow(0 14px 30px rgba(0,0,0,0.45))',
      }}
    >
      {children}
    </div>
  );
}

/** Generic beat-gated wrapper: children pop/slide in when local >= at. */
export function Reveal({
  at,
  local,
  dur = 0.5,
  rise = 40,
  from = 0.5,
  children,
  style,
}: {
  at: number;
  local: number;
  dur?: number;
  rise?: number;
  from?: number;
  children: ReactNode;
  style?: CSSProperties;
}) {
  const p = beat(local, at, dur);
  return (
    <div
      style={{
        opacity: p,
        transform: `translateY(${(1 - p) * rise}px) scale(${from + (1 - from) * p})`,
        ...style,
      }}
    >
      {children}
    </div>
  );
}
