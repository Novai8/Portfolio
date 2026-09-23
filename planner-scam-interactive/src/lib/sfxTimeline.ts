/**
 * sfxTimeline hook — fires scheduled SFX events exactly when the audio clock
 * crosses their timestamp. Seeks re-arm the pointer; big forward jumps don't
 * machine-gun every skipped event.
 */
import { useEffect, useRef } from 'react';
import sfxTimeline from '../data/sfx_timeline.json';
import { sfx, type SfxEvent } from './sfxManager';

const EVENTS = (sfxTimeline as SfxEvent[]).slice().sort((a, b) => a.time - b.time);

export function useSfxScheduler(time: number, playing: boolean) {
  const ptr = useRef(0);
  const last = useRef(0);

  useEffect(() => {
    if (time < last.current - 0.25) {
      // seeked backwards → re-arm from the new position
      let lo = 0;
      let hi = EVENTS.length - 1;
      while (lo <= hi) {
        const mid = (lo + hi) >> 1;
        if (EVENTS[mid].time <= time) lo = mid + 1;
        else hi = mid - 1;
      }
      ptr.current = lo;
    } else if (time > last.current + 2.5) {
      // big forward jump (seek) → skip events silently
      let lo = 0;
      let hi = EVENTS.length - 1;
      while (lo <= hi) {
        const mid = (lo + hi) >> 1;
        if (EVENTS[mid].time <= time) lo = mid + 1;
        else hi = mid - 1;
      }
      ptr.current = lo;
    } else {
      while (ptr.current < EVENTS.length && EVENTS[ptr.current].time <= time) {
        const ev = EVENTS[ptr.current];
        if (time - ev.time < 1.0 && playing) sfx.trigger(ev.sfx);
        ptr.current++;
      }
    }
    last.current = time;
  }, [time, playing]);
}
