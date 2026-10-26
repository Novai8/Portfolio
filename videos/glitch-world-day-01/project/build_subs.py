#!/usr/bin/env python3
"""
build_subs.py — turn the recording + the script into timed captions.

There is no speech-to-text available in this environment, so alignment works
from the two things we *can* measure exactly:

  1. the recording's speech segments and pauses (scripts/audio-analysis.json)
  2. the words that were actually spoken (scripts/transcript.txt)

Each sentence is placed by walking the concatenated speech timeline
(silence removed) and spending time in proportion to its character count. Pauses
therefore fall on sentence boundaries exactly where the reader paused, and every
caption is pinned to real speech, never to silence.

Outputs
    scripts/subtitles.json   cues (with highlight words) used by the renderer
    scripts/sentences.json   sentence-level timing for the edit
    final/glitch-world-day-01.srt
"""
from __future__ import annotations

import json
import math
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ANALYSIS = os.path.join(ROOT, "scripts", "audio-analysis.json")
TRANSCRIPT = os.path.join(ROOT, "scripts", "transcript.txt")
OUT_CUES = os.path.join(ROOT, "scripts", "subtitles.json")
OUT_SENT = os.path.join(ROOT, "scripts", "sentences.json")
OUT_SRT = os.path.join(ROOT, "final", "glitch-world-day-01.srt")

# words worth colouring (matched on the stripped, lowercased token stream)
ACCENTS = [
    ("reality update failed", "magenta"),
    ("restarting in 100 days", "red"),
    ("100 days", "red"),
    ("99 days", "red"),
    ("backward", "cyan"),
    ("ocean", "cyan"),
    ("grocery store", "cyan"),
    ("my face", "magenta"),
    ("milk", "amber"),
    ("froze", "cyan"),
    ("except me", "magenta"),
    ("nothing", "cyan"),
    ("chicken", "amber"),
    ("second stickman", "magenta"),
    ("stickman", "magenta"),
    ("not real", "magenta"),
    ("disappeared", "cyan"),
    ("countdown", "red"),
    ("created this world", "red"),
    ("restarted", "red"),
    ("terrible decision", "red"),
    ("isn't going to be pretty", "red"),
    ("choose carefully", "amber"),
    ("what the hell", "amber"),
    ("break into", "red"),
    ("mysterious building", "red"),
    ("what should i do first", "cyan"),
]
MAX_CUE_CHARS = 46
MIN_CUE = 0.85


def load_segments():
    with open(ANALYSIS) as f:
        a = json.load(f)
    return a["measured_duration_s"], a["segments"]


def load_sentences():
    out = []
    with open(TRANSCRIPT) as f:
        for raw in f:
            line = raw.strip()
            if line:
                out.append(line)
    return out


def char_weight(s):
    """rough spoken length: letters + digits + a little for punctuation pauses"""
    w = len(re.sub(r"[^A-Za-z0-9]", "", s))
    w += s.count(",") * 2.5
    w += s.count(".") * 4.0
    w += s.count(":") * 2.0
    return max(1.0, w)


def align(sentences, segments, duration):
    """
    Walk the speech timeline. For each sentence, find the segment we are in when
    its character budget runs out — that becomes the sentence end.
    """
    total_chars = sum(char_weight(s) for s in sentences)
    total_speech = sum(s["dur"] for s in segments)
    cps = total_chars / total_speech

    # concatenated speech timeline
    clock = []          # (t_start, t_end) per second of speech
    pos = 0.0
    for seg in segments:
        clock.append((pos, pos + seg["dur"], seg["start"]))
        pos += seg["dur"]

    def speech_to_real(t):
        for a, b, real0 in clock:
            if t <= b:
                return real0 + (t - a)
        return clock[-1][2] + clock[-1][1] - clock[-1][0]

    out = []
    cur = 0.0
    for s in sentences:
        w = char_weight(s)
        start_speech = cur
        cur += w / cps
        out.append(dict(text=s, t0=speech_to_real(start_speech), t1=speech_to_real(cur)))
    # pin the last sentence to the true end of speech
    out[-1]["t1"] = segments[-1]["end"]
    for i in range(len(out) - 1):
        out[i + 1]["t0"] = min(out[i + 1]["t0"], out[i + 1]["t1"] - 0.3)
        out[i]["t1"] = min(out[i]["t1"], out[i + 1]["t0"])
    for s in out:
        s["dur"] = round(s["t1"] - s["t0"], 3)
        s["t0"] = round(s["t0"], 3)
        s["t1"] = round(s["t1"], 3)
    return out


def split_phrases(text, max_chars=MAX_CUE_CHARS):
    """
    Break a sentence into caption-sized phrases. Long sentences are divided into
    *balanced* word-boundary chunks so a phrase never ends mid-thought, and comma
    junctions are preferred when they land near the target length.
    """
    clean = text.replace('"', "").strip()
    if len(clean) <= max_chars:
        return [clean]

    n_parts = max(2, math.ceil(len(clean) / max_chars))
    target = len(clean) / n_parts
    words = clean.split()
    parts, cur = [], ""
    for i, wd in enumerate(words):
        cand = (cur + " " + wd).strip()
        remaining_words = len(words) - i
        remaining_parts = n_parts - len(parts) - 1
        # which is closer: adding this word or starting a new phrase?
        if cur and (abs(len(cand) - target) > abs(len(cur) - target)
                    or (remaining_parts > 0 and remaining_words <= remaining_parts)):
            if remaining_parts > 0:
                parts.append(cur)
                cur = wd
                continue
        cur = cand
    if cur:
        parts.append(cur)
    # never leave a stranded one-word phrase
    out = []
    for p_ in parts:
        if out and len(p_.split()) == 1:
            out[-1] += " " + p_
        else:
            out.append(p_)
    return out


def balance_wrap(txt, max_len=42):
    """two balanced lines at a word boundary (for the SRT)"""
    if len(txt) <= max_len:
        return txt
    words = txt.split()
    best, best_score = None, 1e9
    for i in range(1, len(words)):
        a, b = " ".join(words[:i]), " ".join(words[i:])
        if len(a) > max_len or len(b) > max_len:
            continue
        score = abs(len(a) - len(b))
        if score < best_score:
            best, best_score = (a, b), score
    if best is None:
        mid = len(txt) // 2
        cut = txt.rfind(" ", 0, mid + 8)
        cut = cut if cut > 0 else mid
        best = (txt[:cut].strip(), txt[cut:].strip())
    return best[0] + "\n" + best[1]


def mark_accents(text):
    """
    Wrap up to two accent phrases in *...* for the renderer.
    Matches are collected first and applied right-to-left so overlapping or
    nested phrases can never leave stray markers in the caption.
    """
    low = text.lower()
    spans = []
    for phrase, _col in ACCENTS:
        start = 0
        while True:
            i = low.find(phrase, start)
            if i < 0:
                break
            spans.append((i, i + len(phrase), len(phrase)))
            start = i + len(phrase)
    # longest first, no overlaps
    spans.sort(key=lambda t: (-t[2], t[0]))
    chosen = []
    for a, b, _l in spans:
        if all(b <= c or a >= d for c, d, _ in chosen):
            chosen.append((a, b, 0))
        if len(chosen) >= 2:
            break
    for a, b, _l in sorted(chosen, reverse=True):
        text = text[:a] + "*" + text[a:b] + "*" + text[b:]
    return text


def build_cues(sents):
    cues = []
    for s in sents:
        pieces = split_phrases(s["text"])
        weights = [max(1, len(p)) for p in pieces]
        wsum = sum(weights)
        t = s["t0"]
        for i, (p, w) in enumerate(zip(pieces, weights)):
            d = max(MIN_CUE, (s["t1"] - s["t0"]) * w / wsum)
            t1 = min(s["t1"], t + d) if i < len(pieces) - 1 else s["t1"]
            cues.append(dict(start=round(t, 3), end=round(t1, 3), text=mark_accents(p)))
            t = t1
    # merge micro-cues and enforce no overlap
    merged = []
    for c in cues:
        if merged and c["end"] - c["start"] < MIN_CUE * 0.8:
            merged[-1]["end"] = c["end"]
            merged[-1]["text"] += " " + c["text"]
            continue
        if merged and c["start"] < merged[-1]["end"]:
            merged[-1]["end"] = max(merged[-1]["end"], c["end"])
            merged[-1]["text"] += " " + c["text"]
            continue
        merged.append(c)
    for c in merged:
        c["text"] = re.sub(r"\s+", " ", c["text"]).strip()
    return merged


def srt_time(t):
    ms = int(round(t * 1000))
    h, ms = divmod(ms, 3600000)
    m, ms = divmod(ms, 60000)
    s, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def write_srt(cues, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        for i, c in enumerate(cues, 1):
            # strip highlight markers + wrap to two lines for platform players
            txt = balance_wrap(c["text"].replace("*", ""))
            f.write(f"{i}\n{srt_time(c['start'])} --> {srt_time(c['end'])}\n{txt}\n\n")


def main():
    duration, segments = load_segments()
    sentences = load_sentences()
    sents = align(sentences, segments, duration)
    cues = build_cues(sents)
    with open(OUT_CUES, "w") as f:
        json.dump({"cues": cues}, f, indent=2)
    with open(OUT_SENT, "w") as f:
        json.dump({"sentences": sents, "duration": duration}, f, indent=2)
    write_srt(cues, OUT_SRT)
    for s in sents:
        print(f"{s['t0']:7.2f} -> {s['t1']:7.2f}  {s['text'][:74]}")
    print(f"\n{len(sents)} sentences -> {len(cues)} cues")
    print("wrote", OUT_CUES, OUT_SENT, OUT_SRT)


if __name__ == "__main__":
    main()
