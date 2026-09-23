import { useEffect, useRef } from 'react';
import gsap from 'gsap';

interface Props {
  sceneIdx: number; // current (target) scene index
}

const EFFECTS: Record<number, 'iris' | 'glitch' | 'flash' | 'wipe' | 'shards' | 'zoom'> = {
  0: 'flash', 1: 'shards', 2: 'flash', 3: 'zoom', 4: 'glitch', 5: 'iris',
  6: 'shards', 7: 'glitch', 8: 'wipe', 9: 'iris', 10: 'wipe', 11: 'glitch',
  12: 'shards', 13: 'zoom', 14: 'shards', 15: 'flash', 16: 'wipe', 17: 'iris',
};

const ACCENTS = ['#00ff88', '#ff006e', '#00c2ff', '#ffd35c', '#8f7bff', '#ff4646', '#5cffd6'];

/**
 * SceneTransition — a short, style-specific overlay burst whenever the story
 * moves to the next scene (iris wipes, glitch bars, light flashes, shard
 * sweeps). Purely decorative; never blocks interaction for long.
 */
export function SceneTransition({ sceneIdx }: Props) {
  const hostRef = useRef<HTMLDivElement>(null);
  const prev = useRef(-1);

  useEffect(() => {
    const host = hostRef.current;
    if (!host || prev.current === sceneIdx) return;
    const isFirst = prev.current === -1;
    prev.current = sceneIdx;
    if (isFirst) return;

    const effect = EFFECTS[sceneIdx] ?? 'flash';
    const accent = ACCENTS[sceneIdx % ACCENTS.length];
    host.innerHTML = '';
    gsap.killTweensOf(host);
    host.style.clipPath = 'none';
    host.style.background = 'transparent';
    host.style.opacity = '1';

    const ctx = gsap.context(() => {
      if (effect === 'iris') {
        host.style.background = `radial-gradient(circle at 50% 50%, transparent 0 24%, ${accent}dd 26% 30%, transparent 32%)`;
        gsap.fromTo(
          host,
          { clipPath: 'circle(0% at 50% 50%)', opacity: 1 },
          { clipPath: 'circle(120% at 50% 50%)', opacity: 0, duration: 0.85, ease: 'power3.inOut' }
        );
      } else if (effect === 'flash') {
        host.style.background = `radial-gradient(80% 80% at 50% 50%, ${accent}cc, ${accent}22 60%, transparent)`;
        gsap.fromTo(
          host,
          { opacity: 0.95 },
          { opacity: 0, duration: 0.7, ease: 'power2.out' }
        );
      } else if (effect === 'glitch') {
        for (let i = 0; i < 14; i++) {
          const bar = document.createElement('div');
          bar.style.cssText = `position:absolute;left:${Math.random() * 100}%;top:${Math.random() * 100}%;width:${8 + Math.random() * 30}%;height:${2 + Math.random() * 7}%;background:${i % 3 === 0 ? accent : '#ffffff'};opacity:0.85;`;
          host.appendChild(bar);
          gsap.fromTo(
            bar,
            { x: (Math.random() - 0.5) * 500, opacity: 0 },
            { x: 0, opacity: 0.9, duration: 0.09, delay: i * 0.022, ease: 'steps(3)' }
          );
          gsap.to(bar, { opacity: 0, duration: 0.2, delay: 0.32 + i * 0.02 });
        }
        gsap.delayedCall(1.0, () => (host.style.opacity = '0'));
      } else if (effect === 'wipe') {
        host.style.background = `linear-gradient(100deg, transparent 0%, ${accent}bb 18%, #ffffff 50%, ${accent}bb 82%, transparent 100%)`;
        gsap.fromTo(
          host,
          { xPercent: -130, skewX: -8 },
          { xPercent: 130, duration: 0.85, ease: 'power3.inOut' }
        );
      } else if (effect === 'shards') {
        for (let i = 0; i < 9; i++) {
          const s = document.createElement('div');
          s.style.cssText = `position:absolute;top:-20%;left:${i * 11.5}%;width:9%;height:140%;background:linear-gradient(180deg, ${accent}ee, #ffffff88);transform:skewX(${(Math.random() - 0.5) * 20}deg);opacity:0;`;
          host.appendChild(s);
          gsap.fromTo(
            s,
            { yPercent: -110, opacity: 0.95 },
            { yPercent: 110, opacity: 0.95, duration: 0.55, delay: i * 0.035, ease: 'power2.inOut' }
          );
          gsap.to(s, { opacity: 0, duration: 0.25, delay: 0.6 + i * 0.03 });
        }
        gsap.delayedCall(1.1, () => (host.style.opacity = '0'));
      } else {
        // zoom: expanding ring
        const ring = document.createElement('div');
        ring.style.cssText = `position:absolute;left:50%;top:50%;width:220px;height:220px;margin:-110px 0 0 -110px;border-radius:50%;border:14px solid ${accent};box-shadow:0 0 80px ${accent}88, inset 0 0 40px ${accent}55;`;
        host.appendChild(ring);
        gsap.fromTo(ring, { scale: 0.1, opacity: 1 }, { scale: 9, opacity: 0, duration: 0.8, ease: 'power3.out' });
      }
    }, host);

    return () => {
      ctx.revert();
    };
  }, [sceneIdx]);

  return (
    <div
      ref={hostRef}
      style={{ position: 'absolute', inset: 0, zIndex: 50, pointerEvents: 'none', opacity: 0 }}
      aria-hidden
    />
  );
}
