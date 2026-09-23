import { useEffect, useRef, useState } from 'react';
import { SCENES, formatTime } from '../lib/audioSync';
import { sfx } from '../lib/sfxManager';

interface Props {
  time: number;
  wordIdx: number;
  sceneIdx: number;
  chunkIdx: number;
  totalSfx: number;
}

/**
 * DebugOverlay — press `D` to toggle. Shows the master clock, active
 * word/scene/chunk indices and live FPS. Press `P` to audition every SFX
 * recipe back-to-back.
 */
export function DebugOverlay({ time, wordIdx, sceneIdx, chunkIdx, totalSfx }: Props) {
  const [on, setOn] = useState(false);
  const [fps, setFps] = useState(60);
  const frames = useRef(0);
  const lastTick = useRef(performance.now());

  useEffect(() => {
    const key = (e: KeyboardEvent) => {
      if (e.key === 'd' || e.key === 'D') setOn((v) => !v);
      if (e.key === 'p' || e.key === 'P') sfx.previewAll(160);
    };
    window.addEventListener('keydown', key);
    return () => window.removeEventListener('keydown', key);
  }, []);

  useEffect(() => {
    let raf = 0;
    const loop = () => {
      frames.current++;
      const now = performance.now();
      if (now - lastTick.current >= 500) {
        setFps(Math.round((frames.current * 1000) / (now - lastTick.current)));
        frames.current = 0;
        lastTick.current = now;
      }
      raf = requestAnimationFrame(loop);
    };
    raf = requestAnimationFrame(loop);
    return () => cancelAnimationFrame(raf);
  }, []);

  if (!on) return null;
  const sc = SCENES[sceneIdx];
  return (
    <div className="debug-overlay">
      <div>⏱ t = {time.toFixed(2)}s ({formatTime(time)})</div>
      <div>scene {sc?.id} “{sc?.name}” [{sc?.start.toFixed(1)} → {sc?.end.toFixed(1)}]</div>
      <div>word #{wordIdx} · chunk #{chunkIdx}</div>
      <div>sfx events scheduled: {totalSfx}</div>
      <div>fps: {fps} · keys: D=debug P=audition sfx</div>
    </div>
  );
}
