import { useEffect, useMemo, useRef } from 'react';
import gsap from 'gsap';
import { WORDS, CHUNKS } from '../lib/audioSync';

interface Props {
  wordIdx: number;
  chunkIdx: number;
  visible: boolean;
}

const SPANS: Record<number, HTMLSpanElement[]> = {};

/**
 * WordHighlight — karaoke-style captions with word-level accuracy.
 * The active word pops (GSAP elastic), spoken words dim, upcoming words glow
 * faintly. Only the words of the current chunk are mounted; the container
 * flips in with a spring when the chunk changes.
 */
export function WordHighlight({ wordIdx, chunkIdx, visible }: Props) {
  const chunk = CHUNKS[Math.max(0, Math.min(CHUNKS.length - 1, chunkIdx))];
  const words = useMemo(
    () => (chunk ? WORDS.slice(chunk.w0, chunk.w1 + 1).map((w) => w.word) : []),
    [chunk]
  );
  const boxRef = useRef<HTMLDivElement>(null);
  const prevChunk = useRef(chunkIdx);

  useEffect(() => {
    if (!boxRef.current) return;
    if (prevChunk.current !== chunkIdx) {
      prevChunk.current = chunkIdx;
      gsap.fromTo(
        boxRef.current,
        { y: 26, opacity: 0, scale: 0.94, rotate: -0.6 },
        { y: 0, opacity: 1, scale: 1, rotate: 0, duration: 0.38, ease: 'back.out(1.6)', overwrite: true }
      );
    }
  }, [chunkIdx]);

  useEffect(() => {
    if (!chunk) return;
    const spans = SPANS[chunk.i] || [];
    spans.forEach((el, i) => {
      const gi = chunk.w0 + i;
      if (!el) return;
      if (gi === wordIdx) {
        gsap.to(el, {
          scale: 1.22,
          y: -4,
          color: '#00ff88',
          opacity: 1,
          duration: 0.16,
          ease: 'back.out(2.2)',
          overwrite: true,
          className: 'caption-word active',
        });
      } else if (gi < wordIdx) {
        gsap.to(el, { scale: 1, y: 0, color: '#96a0bd', opacity: 0.8, duration: 0.12, overwrite: true, className: 'caption-word spoken' });
      } else {
        gsap.to(el, { scale: 1, y: 0, color: '#e8ecff', opacity: 0.34, duration: 0.12, overwrite: true, className: 'caption-word' });
      }
    });
  }, [wordIdx, chunk]);

  if (!chunk) return null;
  return (
    <div className="captions-wrap" style={{ opacity: visible ? 1 : 0, transition: 'opacity 0.3s' }}>
      <div ref={boxRef} className="caption-chunk">
        {words.map((w, i) => (
          <span
            key={`${chunk.i}-${i}`}
            ref={(el) => {
              if (!SPANS[chunk.i]) SPANS[chunk.i] = [];
              SPANS[chunk.i][i] = el!;
            }}
            className="caption-word"
          >
            {w}
          </span>
        ))}
      </div>
    </div>
  );
}
