#!/usr/bin/env python3
"""
Audio analysis for Glitch World Day 02.

Inputs  : source voiceover MP3 (authoritative, untouched)
Outputs : voiceover-timing.json (sentences, pauses, beats, subtitle cues)
          day-02-he-knows-my-name.srt
Tools   : ffmpeg silencedetect + offline PocketSphinx word timestamps,
          fused with the canonical reference script through sequence
          alignment (difflib). No cloud ASR, no re-voicing.
"""
import json, os, re, subprocess, difflib, sys, shutil

import pocketsphinx as ps

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
SRC_MP3 = os.path.join(ROOT, "assets", "audio", "source", "day-02-voiceover-source.mp3")
WAV16 = "/tmp/wav/day2_16k.wav"
FFMPEG = shutil.which("ffmpeg")
if not FFMPEG:
    import imageio_ffmpeg
    FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()

# ---------------------------------------------------------------- canonical script
# Each entry = one narrative sentence / subtitle cue, matched to the recording.
SENTENCES = [
    "Yesterday, I found out that my world was going to restart in 100 days.",
    "Then some random stickman looked me dead in the eyes and told me I wasn't real.",
    "Naturally, I decided to find him.",
    "The problem? He had literally vanished into thin air.",
    "I spent the next six hours searching the city, following strange glitches that appeared whenever I got close to something unusual.",
    "A streetlight flickered whenever I walked underneath it.",
    "Every clock showed 11:11.",
    "And one building had my apartment number on every single door.",
    "Then I found a message scratched into a wall.",
    "STOP LOOKING FOR ME.",
    "Great. A mysterious warning from a guy who apparently doesn't believe in privacy.",
    "I was about to leave when another message appeared beneath it.",
    "LOOK UP.",
    "So I did.",
    "There he was, standing on top of a building that definitely hadn't existed five seconds earlier.",
    "I ran upstairs, nearly fell through a staircase that kept changing direction, and finally reached the roof.",
    "He was waiting for me.",
    "I asked him the obvious question.",
    "Who are you?",
    "He looked at me and said, I'm the reason you're still alive.",
    "Before I could ask what that meant, he grabbed my arm and showed me something on his wrist.",
    "A countdown.",
    "The exact same countdown floating above my head.",
    "Except his didn't say 98 days.",
    "It said zero.",
    "Then the sky started breaking apart.",
    "He looked straight at me and whispered, when the timer reaches zero, the world doesn't restart.",
    "He paused.",
    "YOU do.",
    "And then every person in the city turned their head toward us at the exact same time.",
    "The mysterious stickman shoved a key into my hand.",
    "Find the room with no door, he said.",
    "And whatever you do, don't trust the version of me you meet tomorrow.",
    "Then he disappeared.",
    "Now I've got a key that opens absolutely nothing, an entire city staring at me, and apparently another version of this guy coming tomorrow.",
    "So what do I do?",
    "A: Search for the room with no door.",
    "B: Find out why everyone in the city is watching me.",
    "Because something tells me this world is hiding a lot more than a few glitches.",
]

# Story beats mapped to cue indices (0-based)
BEATS = {
    "scene1_search_begins": [0, 1, 2, 3],
    "scene2_montage": [4, 5, 6, 7],
    "scene3_first_warning": [8, 9, 10],
    "scene4_second_message": [11, 12, 13],
    "scene5_building_reveal": [14],
    "scene6_impossible_staircase": [15],
    "scene7_rooftop_confrontation": [16, 17, 18],
    "scene9_alive_revelation": [19],
    "scene10_zero_countdown": [20, 21, 22, 23, 24],
    "scene11_sky_breaks": [25, 26],
    "scene12_you_do_twist": [27, 28],
    "scene13_city_turns": [29],
    "scene14_15_key_and_room": [30, 31],
    "scene16_warning_tomorrow": [32],
    "scene17_disappearance": [33],
    "scene18_isolation": [34],
    "scene19_choices": [35, 36, 37, 38],
}

def norm(w):
    return re.sub(r"[^a-z0-9]", "", w.lower())

def words_of(s):
    return [norm(w) for w in re.findall(r"[A-Za-z0-9:]+", s) if norm(w)]

# ------------------------------------------------------------ 1. ffmpeg silences
def detect_silences():
    cmd = [FFMPEG, "-hide_banner", "-nostats", "-i", SRC_MP3,
           "-af", "silencedetect=noise=-32dB:d=0.30", "-f", "null", "-"]
    out = subprocess.run(cmd, capture_output=True, text=True).stderr
    starts, ends = [], []
    for line in out.splitlines():
        m = re.search(r"silence_start: ([\d.]+)", line)
        if m: starts.append(float(m.group(1)))
        m = re.search(r"silence_end: ([\d.]+) \| silence_duration: ([\d.]+)", line)
        if m: ends.append((float(m.group(1)), float(m.group(2))))
    dm = re.search(r"Duration: (\d+):(\d+):([\d.]+)", out)
    dur = int(dm.group(1)) * 3600 + int(dm.group(2)) * 60 + float(dm.group(3))
    ivals = []
    for i, st in enumerate(starts):
        en = ends[i][0] if i < len(ends) else dur
        ivals.append((st, en))
    return ivals, dur

# ------------------------------------------------------------ 2. pocketsphinx words
def ps_words():
    base = os.path.join(os.path.dirname(ps.__file__), "model", "en-us")
    dec = ps.Decoder(hmm=os.path.join(base, "en-us"),
                     lm=os.path.join(base, "en-us.lm.bin"),
                     dict=os.path.join(base, "cmudict-en-us.dict"))
    raw = open(WAV16, "rb").read()[44:]
    dec.start_utt()
    dec.process_raw(raw, False, True)
    dec.end_utt()
    out = []
    for seg in dec.seg():
        w = norm(seg.word)
        if w and w not in ("<s>", "</s>", "[noise]", "<sil>"):
            # pocketsphinx frames: 1/100 s
            out.append((w, seg.start_frame / 100.0, seg.end_frame / 100.0))
    return out

# ------------------------------------------------------------ 3. sequence alignment
def align(ref_words, hyp):
    hyp_words = [w for w, _, _ in hyp]
    sm = difflib.SequenceMatcher(a=ref_words, b=hyp_words, autojunk=False)
    # ref word index -> hyp time (midpoint); unmatched get None
    ref_time = [None] * len(ref_words)
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag in ("equal", "replace"):
            for k in range(i2 - i1):
                hj = j1 + min(k, j2 - j1 - 1)
                ref_time[i1 + k] = (hyp[hj][1] + hyp[hj][2]) / 2
        # delete/insert: leave None, interpolate later
    # fill None by linear interpolation between anchored points
    anchored = [(i, t) for i, t in enumerate(ref_time) if t is not None]
    for i in range(len(ref_time)):
        if ref_time[i] is None:
            prev = max((a for a in anchored if a[0] < i), default=None)
            nxt = min((a for a in anchored if a[0] > i), default=None)
            if prev and nxt:
                frac = (i - prev[0]) / max(1, nxt[0] - prev[0])
                ref_time[i] = prev[1] + frac * (nxt[1] - prev[1])
            elif prev:
                ref_time[i] = prev[1] + 0.25
            elif nxt:
                ref_time[i] = max(0.0, nxt[1] - 0.25)
    return ref_time

def snap_to_silence(t, silences, direction, max_shift=0.45):
    for st, en in silences:
        if direction == "start":
            if st <= t <= en: return en
            if 0 < st - t <= max_shift: return st
        else:
            if st <= t <= en: return st
            if 0 < t - en <= max_shift: return en
    return t

def srt_time(t):
    h = int(t // 3600); m = int((t % 3600) // 60); s = t % 60
    return f"{h:02d}:{m:02d}:{int(s):02d},{int(round((s - int(s)) * 1000)):03d}"

def main():
    if not os.path.exists(WAV16):
        subprocess.run([FFMPEG, "-y", "-v", "error", "-i", SRC_MP3,
                        "-ac", "1", "-ar", "16000", WAV16], check=True)
    silences, duration = detect_silences()
    hyp = ps_words()
    ref_words, word_owner = [], []
    for si, sent in enumerate(SENTENCES):
        for w in words_of(sent):
            ref_words.append(w); word_owner.append(si)
    times = align(ref_words, hyp)

    cues = []
    for si, sent in enumerate(SENTENCES):
        idxs = [i for i, o in enumerate(word_owner) if o == si]
        first, last = idxs[0], idxs[-1]
        # word duration estimate from neighbouring words
        w0 = max(0.0, times[first] - 0.18)
        w1 = min(duration, times[last] + 0.30)
        start = snap_to_silence(w0, silences, "start")
        end = snap_to_silence(w1, silences, "end")
        end = max(end, start + 0.5)
        cues.append({"index": si, "text": sent, "start": round(start, 3),
                     "end": round(end, 3)})
    # enforce monotonic non-overlap
    for i in range(1, len(cues)):
        if cues[i]["start"] < cues[i - 1]["end"] + 0.02:
            cues[i]["start"] = round(cues[i - 1]["end"] + 0.02, 3)
        if cues[i]["end"] <= cues[i]["start"]:
            cues[i]["end"] = round(cues[i]["start"] + 0.5, 3)

    pauses = [{"start": round(a, 3), "end": round(b, 3), "duration": round(b - a, 3)}
              for a, b in silences if b - a >= 0.30]

    timing = {
        "source_file": "assets/audio/source/day-02-voiceover-source.mp3",
        "google_drive_id": "1gzTUpggyWjk-QiLz-9kEojlEl95YOB_u",
        "google_drive_name": "ElevenLabs_2026-10-26T15_26_39_Adam - Radio Announcer_pvc_sp100_s45_sb55_v4.mp3",
        "drive_created_time": "2026-10-26T15:27:58.539Z",
        "drive_modified_time": "2026-10-26T15:27:24.660Z",
        "sample_rate_hz": 44100,
        "channels": 1,
        "bitrate_bps": 128000,
        "measured_duration_s": round(duration, 3),
        "analysis": "ffmpeg silencedetect(-32dB,0.30s) fused with offline PocketSphinx word timestamps via difflib alignment to the canonical Day 2 script",
        "sentences": cues,
        "pauses": pauses,
        "story_beats": {k: [cues[i] for i in v] for k, v in BEATS.items()},
    }
    with open(os.path.join(ROOT, "voiceover-timing.json"), "w") as f:
        json.dump(timing, f, indent=2)

    # SRT — merge long cues into max 2 lines at render time; here keep sentence cues,
    # wrapping long text visually in the player/burn-in.
    srt = []
    for n, c in enumerate(cues, 1):
        srt.append(f"{n}\n{srt_time(c['start'])} --> {srt_time(c['end'])}\n{c['text']}\n")
    with open(os.path.join(ROOT, "day-02-he-knows-my-name.srt"), "w") as f:
        f.write("\n".join(srt))
    print("cues:", len(cues), "duration:", duration, "pauses>=0.3s:", len(pauses))
    for c in cues:
        print(f"{c['index']:2d} {c['start']:7.3f}-{c['end']:7.3f}  {c['text'][:60]}")

if __name__ == "__main__":
    main()
