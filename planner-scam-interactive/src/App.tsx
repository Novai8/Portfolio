import { useCallback, useEffect, useRef, useState } from 'react';
import { AnimatePresence, motion } from 'framer-motion';
import { useShowClock, SCENES, formatTime } from './lib/audioSync';
import { useSfxScheduler } from './lib/sfxTimeline';
import { sfx } from './lib/sfxManager';
import { MotionBackground } from './components/MotionBackground';
import { WordHighlight } from './components/WordHighlight';
import { SceneTransition } from './components/SceneTransition';
import { InteractiveUI } from './components/InteractiveUI';
import { DebugOverlay } from './components/DebugOverlay';
import sfxTimelineData from './data/sfx_timeline.json';

import { Scene01 } from './scenes/Scene01_LateNight';
import { Scene02 } from './scenes/Scene02_PlannerBusiness';
import { Scene03 } from './scenes/Scene03_DashboardRefresh';
import { Scene04 } from './scenes/Scene04_BigReveal';
import { Scene05 } from './scenes/Scene05_HeartParkour';
import { Scene06 } from './scenes/Scene06_WarehouseNoir';
import { Scene07 } from './scenes/Scene07_Possibilities';
import { Scene08 } from './scenes/Scene08_EmailExchange';
import { Scene09 } from './scenes/Scene09_BrainSpiral';
import { Scene10 } from './scenes/Scene10_LivingRoomOffice';
import { Scene11 } from './scenes/Scene11_MayaCall';
import { Scene12 } from './scenes/Scene12_Investigation';
import { Scene13 } from './scenes/Scene13_Escalation';
import { Scene14 } from './scenes/Scene14_PaymentCall';
import { Scene15 } from './scenes/Scene15_ThreatRansom';
import { Scene16 } from './scenes/Scene16_Lockdown';
import { Scene17 } from './scenes/Scene17_Laughter';
import { Scene18 } from './scenes/Scene18_HappyEnding';

const SCENE_COMPONENTS = [
  Scene01, Scene02, Scene03, Scene04, Scene05, Scene06, Scene07, Scene08,
  Scene09, Scene10, Scene11, Scene12, Scene13, Scene14, Scene15, Scene16,
  Scene17, Scene18,
];

export default function App() {
  const audioRef = useRef<HTMLAudioElement>(null);
  const { state, play, toggle, seek, seekBy } = useShowClock(audioRef);
  const [started, setStarted] = useState(false);
  const [captionsOn, setCaptionsOn] = useState(true);
  const [sfxOn, setSfxOn] = useState(true);
  const [scale, setScale] = useState(1);
  const prevScene = useRef(-1);

  const { time, playing, duration, wordIdx, sceneIdx, chunkIdx } = state;
  useSfxScheduler(time, playing);

  // stage scaling (1600×900 design space → fit any viewport, mobile included)
  useEffect(() => {
    const fit = () => {
      const vw = window.innerWidth;
      const vh = window.innerHeight;
      setScale(Math.min(vw / 1620, vh / 940));
    };
    fit();
    window.addEventListener('resize', fit);
    document.addEventListener('fullscreenchange', fit);
    return () => {
      window.removeEventListener('resize', fit);
      document.removeEventListener('fullscreenchange', fit);
    };
  }, []);

  // subtle whoosh on every scene boundary + remember transitions
  useEffect(() => {
    if (prevScene.current !== -1 && prevScene.current !== sceneIdx && playing) {
      sfx.trigger('whoosh');
    }
    prevScene.current = sceneIdx;
  }, [sceneIdx, playing]);

  // keyboard shortcuts
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (e.code === 'Space') { e.preventDefault(); if (started) toggle(); }
      if (e.code === 'ArrowLeft') seekBy(-10);
      if (e.code === 'ArrowRight') seekBy(10);
      if (e.key === 'c' || e.key === 'C') setCaptionsOn((v) => !v);
      if (e.key === 'm' || e.key === 'M') setSfxOn((v) => !v);
    };
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, [toggle, seekBy, started]);

  const begin = useCallback(() => {
    sfx.resume();
    setStarted(true);
    play();
  }, [play]);

  const ended = duration > 0 && time >= duration - 0.35;

  return (
    <div className="viewport">
      <audio ref={audioRef} src="assets/audio/voiceover.mp3" preload="auto" />

      <div className="stage" style={{ transform: `scale(${scale})` }}>
        <MotionBackground sceneIdx={sceneIdx} playing={playing} />

        {SCENES.map((s, i) => {
          const Scene = SCENE_COMPONENTS[i];
          const active = sceneIdx === i && !ended;
          return (
            <div key={s.id} className={`scene${active ? ' active' : ''}`}>
              <Scene
                active={active}
                local={Math.max(0, time - s.start)}
                g={time}
                wordIdx={wordIdx}
                chunkIdx={chunkIdx}
              />
            </div>
          );
        })}

        <SceneTransition sceneIdx={sceneIdx} />

        <WordHighlight wordIdx={wordIdx} chunkIdx={chunkIdx} visible={captionsOn && started && !ended} />

        {/* end card */}
        <AnimatePresence>
          {ended && (
            <motion.div
              className="endcard"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.8 }}
            >
              <div className="start-kicker">THE END</div>
              <div className="start-title" style={{ fontSize: 84 }}>SHIP YOUR SPINE FIRST 🦴</div>
              <div className="start-sub">
                A true story about a 2:07 a.m. order, an abandoned warehouse,
                and the night I learned that “verify reality” beats “worship big numbers.”
              </div>
              <button className="start-btn" onClick={() => { seek(0); setTimeout(play, 60); }}>
                ↺ REPLAY THE STORY
              </button>
              <div className="start-hint">an interactive motion story · {formatTime(duration)} · 18 scenes · word-synced</div>
            </motion.div>
          )}
        </AnimatePresence>

        <DebugOverlay time={time} wordIdx={wordIdx} sceneIdx={sceneIdx} chunkIdx={chunkIdx} totalSfx={sfxTimelineData.length} />

        {started && (
          <InteractiveUI
            time={time}
            duration={duration}
            playing={playing}
            sceneIdx={sceneIdx}
            captionsOn={captionsOn}
            sfxOn={sfxOn}
            onToggle={toggle}
            onSeek={seek}
            onSeekBy={seekBy}
            onToggleCaptions={() => setCaptionsOn((v) => !v)}
            onToggleSfx={() => {
              setSfxOn((v) => {
                sfx.setEnabled(!v);
                return !v;
              });
            }}
          />
        )}

        {/* start overlay */}
        <AnimatePresence>
          {!started && (
            <motion.div
              className="start-overlay"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0, scale: 1.06, filter: 'blur(6px)' }}
              transition={{ duration: 0.5 }}
              onClick={begin}
            >
              <div className="start-kicker">AN INTERACTIVE MOTION STORY · WORD-SYNCED</div>
              <div className="start-title">
                THE 2:07 A.M.<br />ORDER
              </div>
              <div className="start-sub">
                500 planners. $12,480. An abandoned warehouse.
                A raccoon-shaped question mark. This is the story of the night
                a “customer” tried to scam my planner shop — and accidentally upgraded it.
              </div>
              <motion.button
                className="start-btn"
                whileHover={{ scale: 1.06 }}
                whileTap={{ scale: 0.96 }}
                onClick={begin}
              >
                ▶ PLAY THE EXPERIENCE
              </motion.button>
              <div className="start-hint">
                10:32 · 18 scenes · 123 synced sound events · space = play/pause · ←/→ = ±10s · C = captions · D = debug
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
}
