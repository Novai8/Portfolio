/**
 * audioSync.ts — the zero-drift master clock.
 *
 * Every visual and audible beat in the experience is derived from the
 * <audio> element's `currentTime`, polled inside a single requestAnimationFrame
 * loop. No wall-clock timers are used for sync, so pausing, seeking and tab
 * throttling can never cause drift between words, scenes and SFX.
 */
import { useEffect, useRef, useState, useCallback } from 'react';
import wordsData from '../data/word_timestamps.json';
import scenesData from '../data/scenes.json';
import chunksData from '../data/chunks.json';

export interface Word { word: string; start: number; end: number; conf: number }
export interface Chunk { i: number; w0: number; w1: number; start: number; end: number; text: string }
export interface SceneInfo { id: number; name: string; title: string; start: number; end: number }

export const WORDS = wordsData as Word[];
export const SCENES = scenesData as SceneInfo[];
export const CHUNKS = chunksData as Chunk[];

export const DURATION =
  WORDS.length > 0 ? WORDS[WORDS.length - 1].end + 0.6 : 0;

const WORD_STARTS = new Float64Array(WORDS.map((w) => w.start));

/** Binary search: index of the word spoken at time `t` (or the next upcoming word). */
export function findWordIndex(t: number): number {
  let lo = 0;
  let hi = WORD_STARTS.length - 1;
  if (t < WORD_STARTS[0]) return 0;
  if (t >= WORD_STARTS[hi]) return hi;
  while (lo <= hi) {
    const mid = (lo + hi) >> 1;
    if (WORD_STARTS[mid] <= t) {
      if (mid === WORD_STARTS.length - 1 || WORD_STARTS[mid + 1] > t) return mid;
      lo = mid + 1;
    } else {
      hi = mid - 1;
    }
  }
  return 0;
}

export function findSceneIndex(t: number): number {
  for (let i = SCENES.length - 1; i >= 0; i--) {
    if (t >= SCENES[i].start) return i;
  }
  return 0;
}

export function findChunkIndex(wordIdx: number): number {
  // chunks are ordered by w0
  let lo = 0;
  let hi = CHUNKS.length - 1;
  while (lo <= hi) {
    const mid = (lo + hi) >> 1;
    const c = CHUNKS[mid];
    if (wordIdx < c.w0) hi = mid - 1;
    else if (wordIdx > c.w1) lo = mid + 1;
    else return mid;
  }
  return Math.max(0, Math.min(CHUNKS.length - 1, lo));
}

export function formatTime(t: number): string {
  const m = Math.floor(t / 60);
  const s = Math.floor(t % 60);
  return `${m}:${s.toString().padStart(2, '0')}`;
}

/** Global time of the first word matching `normalized text` (used by SFX timeline UI). */
export function wordTimeByText(text: string): number | null {
  const n = (s: string) => s.toLowerCase().replace(/[^a-z0-9]/g, '');
  const target = n(text);
  for (const w of WORDS) {
    if (n(w.word) === target) return w.start;
  }
  return null;
}

export interface ShowState {
  time: number;
  playing: boolean;
  duration: number;
  ready: boolean;
  wordIdx: number;
  sceneIdx: number;
  chunkIdx: number;
}

/**
 * The single source of truth for the whole experience.
 * Updates are quantized to 30 Hz for React state (GSAP/canvas animations run at
 * full display refresh independently), which keeps React overhead low while the
 * visuals stay perfectly locked to the audio clock.
 */
export function useShowClock(audioRef: React.RefObject<HTMLAudioElement | null>): {
  state: ShowState;
  play: () => void;
  pause: () => void;
  toggle: () => void;
  seek: (t: number) => void;
  seekBy: (d: number) => void;
} {
  const [state, setState] = useState<ShowState>({
    time: 0,
    playing: false,
    duration: DURATION,
    ready: false,
    wordIdx: 0,
    sceneIdx: 0,
    chunkIdx: 0,
  });
  const raf = useRef(0);
  const lastQ = useRef(-1);

  useEffect(() => {
    const loop = () => {
      const a = audioRef.current;
      if (a) {
        const t = a.currentTime;
        const q = Math.round(t * 30) / 30; // 30 Hz quantization for React
        if (q !== lastQ.current) {
          lastQ.current = q;
          const wordIdx = findWordIndex(t);
          const sceneIdx = findSceneIndex(t);
          setState((prev) =>
            prev.time === q &&
            prev.playing === (!a.paused && !a.ended) &&
            prev.ready === (a.readyState >= 2)
              ? prev
              : {
                  ...prev,
                  time: q,
                  playing: !a.paused && !a.ended,
                  ready: a.readyState >= 2,
                  duration: isFinite(a.duration) && a.duration > 0 ? a.duration : DURATION,
                  wordIdx,
                  sceneIdx,
                  chunkIdx: findChunkIndex(wordIdx),
                }
          );
        }
      }
      raf.current = requestAnimationFrame(loop);
    };
    raf.current = requestAnimationFrame(loop);
    return () => cancelAnimationFrame(raf.current);
  }, [audioRef]);

  const play = useCallback(() => {
    const a = audioRef.current;
    if (!a) return;
    a.volume = 1;
    void a.play().catch(() => undefined);
  }, [audioRef]);

  const pause = useCallback(() => audioRef.current?.pause(), [audioRef]);

  const toggle = useCallback(() => {
    const a = audioRef.current;
    if (!a) return;
    if (a.paused) void a.play().catch(() => undefined);
    else a.pause();
  }, [audioRef]);

  const seek = useCallback(
    (t: number) => {
      const a = audioRef.current;
      if (!a) return;
      a.currentTime = Math.max(0, Math.min(a.duration || DURATION, t));
      lastQ.current = -1; // force state refresh
    },
    [audioRef]
  );

  const seekBy = useCallback((d: number) => {
    const a = audioRef.current;
    if (!a) return;
    seek(a.currentTime + d);
  }, [seek, audioRef]);

  return { state, play, pause, toggle, seek, seekBy };
}
