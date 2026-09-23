import { useMemo, useRef, useState } from 'react';
import { AnimatePresence, motion } from 'framer-motion';
import { SCENES, formatTime } from '../lib/audioSync';
import { PALETTES } from '../lib/animationHelpers';

interface Props {
  time: number;
  duration: number;
  playing: boolean;
  sceneIdx: number;
  captionsOn: boolean;
  sfxOn: boolean;
  onToggle: () => void;
  onSeek: (t: number) => void;
  onSeekBy: (d: number) => void;
  onToggleCaptions: () => void;
  onToggleSfx: () => void;
}

/**
 * InteractiveUI — the control dock: play/pause, ±10s, a chapter-segmented
 * scrub bar with hover tooltips, chapter menu, caption + SFX toggles,
 * fullscreen. Framer Motion handles the dock & popover micro-interactions.
 */
export function InteractiveUI(props: Props) {
  const { time, duration, playing, sceneIdx, captionsOn, sfxOn } = props;
  const [hover, setHover] = useState<{ x: number; label: string } | null>(null);
  const [chaptersOpen, setChaptersOpen] = useState(false);
  const scrubRef = useRef<HTMLDivElement>(null);
  const dragging = useRef(false);

  const segs = useMemo(() => {
    const total = SCENES[SCENES.length - 1].end || duration;
    return SCENES.map((s, i) => ({
      id: s.id,
      name: s.name,
      start: s.start,
      end: s.end,
      width: ((s.end - s.start) / total) * 100,
      color: Object.values(PALETTES)[i]?.accent ?? '#00ff88',
    }));
  }, [duration]);

  const pct = duration > 0 ? (time / duration) * 100 : 0;

  const seekFromEvent = (clientX: number) => {
    const el = scrubRef.current;
    if (!el) return;
    const rect = el.getBoundingClientRect();
    const frac = Math.max(0, Math.min(1, (clientX - rect.left) / rect.width));
    props.onSeek(frac * duration);
  };

  return (
    <motion.div
      className="dock"
      initial={{ y: 90, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ delay: 0.5, type: 'spring', stiffness: 160, damping: 20 }}
    >
      <button className="dock-btn primary" onClick={props.onToggle} aria-label={playing ? 'Pause' : 'Play'}>
        {playing ? '❚❚' : '▶'}
      </button>
      <button className="dock-btn" onClick={() => props.onSeekBy(-10)} aria-label="Back 10 seconds">⏪</button>
      <button className="dock-btn" onClick={() => props.onSeekBy(10)} aria-label="Forward 10 seconds">⏩</button>

      <div className="dock-time">{formatTime(time)} / {formatTime(duration)}</div>

      <div
        ref={scrubRef}
        className="scrub"
        onPointerDown={(e) => {
          dragging.current = true;
          (e.target as HTMLElement).setPointerCapture?.(e.pointerId);
          seekFromEvent(e.clientX);
        }}
        onPointerMove={(e) => {
          if (dragging.current) seekFromEvent(e.clientX);
          const el = scrubRef.current;
          if (el) {
            const rect = el.getBoundingClientRect();
            const frac = Math.max(0, Math.min(1, (e.clientX - rect.left) / rect.width));
            const t = frac * duration;
            const sc = SCENES.find((s) => t >= s.start && t < s.end) ?? SCENES[0];
            setHover({ x: frac * rect.width, label: `${sc.id}. ${sc.name} · ${formatTime(t)}` });
          }
        }}
        onPointerUp={() => (dragging.current = false)}
        onPointerLeave={() => {
          dragging.current = false;
          setHover(null);
        }}
      >
        <div className="scrub-track">
          {segs.map((s) => (
            <div key={s.id} className="scrub-seg" style={{ width: `${s.width}%`, background: s.color }} />
          ))}
          <div className="scrub-fill" style={{ width: `${pct}%` }} />
        </div>
        <div className="scrub-knob" style={{ left: `${pct}%` }} />
        {hover && (
          <div className="scrub-tip" style={{ left: hover.x }}>
            {hover.label}
          </div>
        )}
      </div>

      <button
        className="dock-btn"
        onClick={props.onToggleCaptions}
        style={{ opacity: captionsOn ? 1 : 0.45 }}
        aria-label="Toggle captions"
      >
        CC
      </button>
      <button
        className="dock-btn"
        onClick={props.onToggleSfx}
        style={{ opacity: sfxOn ? 1 : 0.45 }}
        aria-label="Toggle sound effects"
      >
        {sfxOn ? '🔊' : '🔇'}
      </button>

      <div style={{ position: 'relative' }}>
        <button
          className="dock-btn"
          onClick={() => setChaptersOpen((v) => !v)}
          aria-label="Chapters"
        >
          ☰
        </button>
        <AnimatePresence>
          {chaptersOpen && (
            <motion.div
              className="chapters-pop"
              initial={{ opacity: 0, y: 14, scale: 0.97 }}
              animate={{ opacity: 1, y: 0, scale: 1 }}
              exit={{ opacity: 0, y: 14, scale: 0.97 }}
              transition={{ duration: 0.18 }}
            >
              {SCENES.map((s, i) => (
                <div
                  key={s.id}
                  className={`chapter-row${i === sceneIdx ? ' current' : ''}`}
                  onClick={() => {
                    props.onSeek(s.start + 0.02);
                    setChaptersOpen(false);
                  }}
                >
                  <span className="chapter-num">{s.id.toString().padStart(2, '0')}</span>
                  <span className="chapter-name">{s.name}</span>
                  <span className="chapter-t">{formatTime(s.start)}</span>
                </div>
              ))}
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      <button
        className="dock-btn"
        onClick={() => {
          const vp = document.querySelector('.viewport');
          if (!document.fullscreenElement) vp?.requestFullscreen?.().catch(() => undefined);
          else document.exitFullscreen?.().catch(() => undefined);
        }}
        aria-label="Fullscreen"
      >
        ⛶
      </button>
    </motion.div>
  );
}
