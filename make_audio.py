"""
make_audio.py  --  generates all the game's sound effects and music as .wav files.

Run once with:  python make_audio.py
It SYNTHESIZES every sound from scratch using only Python's standard library
(no downloads, no extra packages). The idea: sound is just a long list of numbers
(samples) describing a speaker's position over time. A sine wave makes a pure
tone; we shape it with a fade-in/out "envelope" so it doesn't click.

Output goes to assets/audio/. Safe to delete this script afterwards; the game
only needs the .wav files it produces.
"""
import os
import wave
import struct
import math

RATE = 22050          # samples per second (CD quality is 44100; this is plenty)
OUT = os.path.join(os.path.dirname(__file__), "assets", "audio")


def write_wav(name, samples):
    """Save a list of float samples (each from -1.0 to 1.0) as a 16-bit WAV."""
    os.makedirs(OUT, exist_ok=True)
    path = os.path.join(OUT, name + ".wav")
    with wave.open(path, "w") as w:
        w.setnchannels(1)        # mono (one channel)
        w.setsampwidth(2)        # 2 bytes = 16-bit samples
        w.setframerate(RATE)
        frames = bytearray()
        for s in samples:
            s = max(-1.0, min(1.0, s))               # never exceed the limits
            frames += struct.pack("<h", int(s * 32767))
        w.writeframes(bytes(frames))
    return path


def tone(freq, dur, vol=0.5, kind="sine", attack=0.005, release=0.04):
    """Build one note: a wave of `freq` Hz for `dur` seconds, with a soft envelope."""
    n = int(RATE * dur)
    out = []
    a = max(1, int(attack * RATE))                   # fade-in length in samples
    r = max(1, int(release * RATE))                  # fade-out length in samples
    for i in range(n):
        t = i / RATE
        if kind == "sine":
            v = math.sin(2 * math.pi * freq * t)
        elif kind == "square":
            v = 1.0 if math.sin(2 * math.pi * freq * t) >= 0 else -1.0
        else:  # "saw"
            v = 2.0 * ((freq * t) % 1.0) - 1.0
        # Envelope: ramp up over `a`, ramp down over the last `r` samples.
        if i < a:
            env = i / a
        elif i > n - r:
            env = max(0.0, (n - i) / r)
        else:
            env = 1.0
        out.append(v * vol * env)
    return out


def silence(dur):
    return [0.0] * int(RATE * dur)


def mix(*tracks):
    """Overlay several equal-ish length sample lists by adding them together."""
    length = max(len(t) for t in tracks)
    out = [0.0] * length
    for t in tracks:
        for i, s in enumerate(t):
            out[i] += s
    return out


# Musical note frequencies (Hz) we'll reuse.
N = {"A3": 220.0, "C4": 261.63, "D4": 293.66, "E4": 329.63, "F4": 349.23,
     "G4": 392.0, "A4": 440.0, "C5": 523.25, "E5": 659.25}


# ---------------------------------------------------------------------------
# SOUND EFFECTS
# ---------------------------------------------------------------------------
def build_effects():
    # A short, bright UI click.
    write_wav("click", tone(900, 0.06, vol=0.35, kind="square", release=0.05))
    # A very soft, quick hover blip.
    write_wav("hover", tone(1300, 0.03, vol=0.12, kind="sine", release=0.025))
    # Success: a happy rising arpeggio C -> E -> G.
    success = tone(523, 0.09, 0.4) + tone(659, 0.09, 0.4) + tone(784, 0.13, 0.4)
    write_wav("success", success)
    # Error: a low, short buzz.
    write_wav("error", tone(150, 0.18, vol=0.4, kind="square"))
    # Win: a longer triumphant fanfare C -> E -> G -> high C.
    win = (tone(523, 0.12, 0.45) + tone(659, 0.12, 0.45) +
           tone(784, 0.12, 0.45) + tone(1047, 0.30, 0.5))
    write_wav("win", win)
    # Select/transition: a quick upward sweep.
    sweep = []
    for i in range(int(RATE * 0.12)):
        t = i / RATE
        f = 400 + 1600 * (t / 0.12)
        sweep.append(math.sin(2 * math.pi * f * t) * 0.25 *
                     max(0.0, 1 - t / 0.12))
    write_wav("select", sweep)


# ---------------------------------------------------------------------------
# BACKGROUND MUSIC  (a soft, looping arpeggio in A minor)
# ---------------------------------------------------------------------------
def build_music():
    # Four chords, each played as a gentle arpeggio. Each chord = (notes, bass).
    chords = [
        (["A3", "C4", "E4", "C4"], 110.0),   # A minor
        (["F4", "A4", "C5", "A4"], 87.31),   # F major
        (["C4", "E4", "G4", "E4"], 130.81),  # C major
        (["G4", "D4", "G4", "E4"], 98.0),    # G major
    ]
    note_len = 0.25                          # each arpeggio note is a quarter beat
    track = []
    for notes, bass_freq in chords:
        # The arpeggio (melody) for this chord.
        melody = []
        for note in notes:
            melody += tone(N[note], note_len, vol=0.16, kind="sine")
        # A soft sustained bass note underneath the whole chord.
        bass = tone(bass_freq, note_len * len(notes), vol=0.12, kind="sine",
                    attack=0.02, release=0.1)
        track += mix(melody, bass)
    write_wav("music", track)                # music.play(-1) will loop this


if __name__ == "__main__":
    build_effects()
    build_music()
    print("Audio written to", OUT)
    for f in sorted(os.listdir(OUT)):
        size = os.path.getsize(os.path.join(OUT, f))
        print(f"  {f:14} {size:>7} bytes")
