#!/usr/bin/env python3
"""
synth_sfx.py — Procedural audio generator for Flutter Game Studio.

Generates REAL, playable audio (16-bit PCM WAV, mono, 44.1 kHz) for every
game-audio event the studio's Sound Design Map defines — no external API,
no .ttf/.ogg encoders, only the Python stdlib. This turns the studio's
AudioService from a graceful-no-op stub into an actually-audible game.

Outputs:
  assets/audio/sfx/sfx_button.wav        — UI tap
  assets/audio/sfx/sfx_navigate.wav      — screen transition swoosh
  assets/audio/sfx/sfx_action.wav        — primary action (spin/tap/launch)
  assets/audio/sfx/sfx_coin.wav          — coin / score tick
  assets/audio/sfx/sfx_error.wav         — invalid / insufficient funds
  assets/audio/sfx/sfx_win_small.wav     — small win
  assets/audio/sfx/sfx_win_big.wav       — big win
  assets/audio/sfx/sfx_win_mega.wav      — mega win
  assets/audio/bgm/bgm_main.wav          — looping background music bed

The "mood" axis (from the game's Design DNA → Emotional Core) selects scale,
tempo and timbre so two games never sound identical.

Usage:
  python3 tools/synth_sfx.py                       # defaults (mood=bright)
  python3 tools/synth_sfx.py --mood dark --seed 7
  python3 tools/synth_sfx.py --from-concept        # infer mood from concept
  python3 tools/synth_sfx.py --list                # list events only
"""

import argparse
import math
import os
import random
import struct
import wave

SAMPLE_RATE = 44100

# ---------------------------------------------------------------------------
# Mood presets — derived from Design DNA emotional core
# ---------------------------------------------------------------------------
# scale: semitone offsets from the root for the BGM arpeggio/pad
# wave:  default oscillator timbre for melodic content
MOODS = {
    "bright":  dict(root=60, scale=[0, 4, 7, 11, 12], bpm=120, wave="triangle", brightness=1.0),
    "dark":    dict(root=53, scale=[0, 3, 7, 10, 12],  bpm=92,  wave="saw",      brightness=0.7),
    "calm":    dict(root=57, scale=[0, 2, 4, 7, 9],    bpm=78,  wave="sine",     brightness=0.85),
    "epic":    dict(root=55, scale=[0, 4, 7, 12, 16],  bpm=108, wave="saw",      brightness=1.0),
    "playful": dict(root=62, scale=[0, 4, 7, 9, 12],   bpm=132, wave="square",   brightness=0.95),
    "tense":   dict(root=51, scale=[0, 1, 6, 7, 10],   bpm=100, wave="square",   brightness=0.6),
}

EVENTS = [
    "sfx_button", "sfx_navigate", "sfx_action", "sfx_coin", "sfx_error",
    "sfx_win_small", "sfx_win_big", "sfx_win_mega", "bgm_main",
]


def midi_to_freq(note: float) -> float:
    return 440.0 * (2.0 ** ((note - 69) / 12.0))


# ---------------------------------------------------------------------------
# Oscillators (return float in [-1, 1] for a given phase in turns)
# ---------------------------------------------------------------------------
def osc(kind: str, phase: float, rng: random.Random) -> float:
    p = phase - math.floor(phase)
    if kind == "sine":
        return math.sin(2 * math.pi * p)
    if kind == "square":
        return 1.0 if p < 0.5 else -1.0
    if kind == "triangle":
        return 4.0 * abs(p - 0.5) - 1.0
    if kind == "saw":
        return 2.0 * p - 1.0
    if kind == "noise":
        return rng.uniform(-1.0, 1.0)
    return math.sin(2 * math.pi * p)


def adsr(i: int, n: int, a: float, d: float, s: float, r: float) -> float:
    """ADSR envelope; a/d/r are fractions of total length, s is sustain level."""
    t = i / max(n - 1, 1)
    if t < a:
        return t / a if a > 0 else 1.0
    if t < a + d:
        return 1.0 - (1.0 - s) * ((t - a) / d if d > 0 else 1.0)
    if t < 1.0 - r:
        return s
    return s * ((1.0 - t) / r if r > 0 else 0.0)


def tone(freq, dur, wave="sine", vol=0.5, a=0.01, d=0.1, s=0.7, r=0.2,
         vibrato=0.0, vib_rate=6.0, pitch_to=None, rng=None):
    """Render a single tone with optional vibrato and linear pitch glide."""
    rng = rng or random.Random(0)
    n = int(dur * SAMPLE_RATE)
    out = [0.0] * n
    phase = 0.0
    for i in range(n):
        t = i / SAMPLE_RATE
        f = freq if pitch_to is None else freq + (pitch_to - freq) * (i / max(n - 1, 1))
        if vibrato:
            f *= 1.0 + vibrato * math.sin(2 * math.pi * vib_rate * t)
        phase += f / SAMPLE_RATE
        out[i] = osc(wave, phase, rng) * adsr(i, n, a, d, s, r) * vol
    return out


def mix(*tracks):
    n = max((len(t) for t in tracks), default=0)
    out = [0.0] * n
    for t in tracks:
        for i, v in enumerate(t):
            out[i] += v
    return out


def concat(*tracks):
    out = []
    for t in tracks:
        out.extend(t)
    return out


def normalize(buf, peak=0.89):
    m = max((abs(v) for v in buf), default=0.0)
    if m < 1e-9:
        return buf
    g = peak / m
    return [v * g for v in buf]


def write_wav(path, buf):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with wave.open(path, "w") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SAMPLE_RATE)
        frames = bytearray()
        for v in buf:
            s = int(max(-1.0, min(1.0, v)) * 32767)
            frames += struct.pack("<h", s)
        w.writeframes(bytes(frames))


# ---------------------------------------------------------------------------
# Event renderers
# ---------------------------------------------------------------------------
def render_event(name, m, rng):
    root, scale, wv, bright = m["root"], m["scale"], m["wave"], m["brightness"]

    if name == "sfx_button":
        return tone(midi_to_freq(root + 24), 0.07, "sine", 0.5,
                    a=0.005, d=0.03, s=0.3, r=0.5, rng=rng)

    if name == "sfx_coin":
        a = tone(midi_to_freq(root + 19), 0.05, "square", 0.4, a=0.002, d=0.02, s=0.4, r=0.4, rng=rng)
        b = tone(midi_to_freq(root + 26), 0.10, "square", 0.4, a=0.002, d=0.05, s=0.3, r=0.6, rng=rng)
        return concat(a, b)

    if name == "sfx_navigate":
        # filtered-ish noise swoosh with a downward pitch feel
        n = int(0.22 * SAMPLE_RATE)
        out = []
        prev = 0.0
        for i in range(n):
            env = adsr(i, n, 0.1, 0.2, 0.5, 0.5)
            raw = rng.uniform(-1, 1) * env
            prev = prev * 0.82 + raw * 0.18  # cheap low-pass
            out.append(prev * 0.6)
        return out

    if name == "sfx_action":
        body = tone(midi_to_freq(root + 5), 0.45, wv, 0.42,
                    a=0.02, d=0.15, s=0.6, r=0.25, vibrato=0.01,
                    pitch_to=midi_to_freq(root + 17), rng=rng)
        shimmer = tone(midi_to_freq(root + 29), 0.45, "sine", 0.12 * bright,
                       a=0.05, d=0.2, s=0.4, r=0.35, rng=rng)
        return normalize(mix(body, shimmer), 0.8)

    if name == "sfx_error":
        a = tone(midi_to_freq(root - 5), 0.18, "square", 0.4, a=0.005, d=0.05, s=0.6, r=0.3, rng=rng)
        b = tone(midi_to_freq(root - 6), 0.18, "square", 0.35, a=0.005, d=0.05, s=0.6, r=0.3, rng=rng)
        return mix(a, b)

    if name in ("sfx_win_small", "sfx_win_big", "sfx_win_mega"):
        tiers = {
            "sfx_win_small": (scale[:3], 0.12, 0.0),
            "sfx_win_big":   (scale + [12], 0.13, 0.18),
            "sfx_win_mega":  (scale + [12, 16, 19], 0.14, 0.45),
        }
        steps, dur, tail = tiers[name]
        arp = concat(*[
            tone(midi_to_freq(root + 12 + st), dur, wv, 0.4,
                 a=0.01, d=0.06, s=0.5, r=0.4, rng=rng)
            for st in steps
        ])
        layers = [arp]
        if tail > 0:
            chord = mix(*[
                tone(midi_to_freq(root + 12 + st), tail + 0.3, "sine", 0.16,
                     a=0.02, d=0.1, s=0.6, r=0.6, rng=rng)
                for st in (0, 4, 7, 12)
            ])
            sparkle = tone(midi_to_freq(root + 36), tail, "triangle", 0.10 * bright,
                           a=0.0, d=0.05, s=0.2, r=0.6, vibrato=0.03, rng=rng)
            layers.append(concat([0.0] * len(arp), mix(chord, sparkle)))
        return normalize(mix(*[l for l in layers]), 0.85)

    if name == "bgm_main":
        return render_bgm(m, rng)

    return tone(midi_to_freq(root), 0.2, "sine", 0.4, rng=rng)


def render_bgm(m, rng):
    """A short, seamless looping bed: bass + arpeggiated pad over 4 chords."""
    root, scale, wv, bright = m["root"], m["scale"], m["wave"], m["brightness"]
    beat = 60.0 / m["bpm"]
    # 4 chords, 2 beats each => 8-beat loop
    degrees = [0, -3, -5, -1] if "dark" in str(scale) else [0, 5, -3, 3]
    chords = [(root - 12 + dg) for dg in degrees]
    pad = []
    bass = []
    arp_notes = scale[:4]
    for ci, base in enumerate(chords):
        chord_len = beat * 2
        # bass: root note held
        bass.append(tone(midi_to_freq(base - 12), chord_len, "triangle", 0.30,
                         a=0.02, d=0.3, s=0.7, r=0.2, rng=rng))
        # pad: arpeggio of 8 sixteenths
        sixteenth = chord_len / 8
        seg = []
        for k in range(8):
            st = arp_notes[k % len(arp_notes)] + (12 if k % 8 >= 4 else 0)
            seg.append(tone(midi_to_freq(base + st), sixteenth, wv, 0.16 * bright,
                            a=0.01, d=0.04, s=0.4, r=0.3, rng=rng))
        pad.append(concat(*seg))
    full = mix(concat(*bass), concat(*pad))
    # tiny fade at the seam so the loop has no click
    n = len(full)
    fade = int(0.01 * SAMPLE_RATE)
    for i in range(fade):
        g = i / fade
        full[i] *= g
        full[n - 1 - i] *= g
    return normalize(full, 0.7)


def infer_mood_from_concept(path="design/gdd/game-concept.md"):
    try:
        with open(path, "r", encoding="utf-8") as f:
            text = f.read().lower()
    except OSError:
        return "bright"
    keys = {
        "dark": ["напряж", "мрач", "нуар", "тревож", "danger", "horror", "dark"],
        "calm": ["спокой", "дзен", "медит", "уют", "calm", "zen", "cozy", "relax"],
        "epic": ["эпич", "epic", "космос", "герой", "boss", "битв"],
        "playful": ["весел", "игрив", "детск", "конфет", "candy", "playful", "cute"],
        "tense": ["казино", "ставк", "риск", "crash", "mines", "gambl"],
    }
    score = {k: 0 for k in keys}
    for mood, words in keys.items():
        for w in words:
            score[mood] += text.count(w)
    best = max(score, key=score.get)
    return best if score[best] > 0 else "bright"


def main():
    ap = argparse.ArgumentParser(description="Procedural game audio synthesizer")
    ap.add_argument("--mood", choices=sorted(MOODS), default=None)
    ap.add_argument("--from-concept", action="store_true",
                    help="infer mood from design/gdd/game-concept.md")
    ap.add_argument("--seed", type=int, default=None)
    ap.add_argument("--sfx-dir", default="assets/audio/sfx")
    ap.add_argument("--bgm-dir", default="assets/audio/bgm")
    ap.add_argument("--list", action="store_true", help="print events and exit")
    args = ap.parse_args()

    if args.list:
        for e in EVENTS:
            print(e)
        return

    mood = args.mood or (infer_mood_from_concept() if args.from_concept else "bright")
    m = MOODS[mood]
    rng = random.Random(args.seed if args.seed is not None else hash(mood) & 0xFFFF)

    made = []
    for name in EVENTS:
        buf = render_event(name, m, rng)
        out_dir = args.bgm_dir if name.startswith("bgm") else args.sfx_dir
        path = os.path.join(out_dir, f"{name}.wav")
        write_wav(path, buf)
        made.append(path)

    print(f"✅ synth_sfx: mood={mood}, {len(made)} files")
    for p in made:
        size = os.path.getsize(p)
        print(f"   {p}  ({size // 1024} KB)")


if __name__ == "__main__":
    main()
