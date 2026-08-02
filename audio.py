"""
audio.py  --  plays the game's sound effects and music.
=======================================================

This wraps pygame's sound system so the rest of the game can just say
audio.play("click") without worrying about the details. Everything is guarded
so that on a computer with no sound (or if a file is missing) the game keeps
running silently instead of crashing.

How sound works in pygame:
    - pygame.mixer.Sound(file)  loads a short sound effect you can .play() anytime.
    - pygame.mixer.music        is a separate channel for ONE long looping track.
"""
import os
import pygame

AUDIO_DIR = os.path.join(os.path.dirname(__file__), "assets", "audio")

# The short sound effects we'll load (each is a .wav in assets/audio).
EFFECT_NAMES = ["click", "hover", "success", "error", "win", "select"]

_sounds = {}          # name -> pygame Sound object
_ready = False        # did the sound system start up successfully?
muted = False         # the player can toggle this with the M key
MUSIC_VOLUME = 0.35   # background music is kept gentle


def init():
    """Start the mixer, load the effects, and begin the music. Safe if it fails."""
    global _ready
    try:
        pygame.mixer.init()
        _ready = True
    except Exception:
        _ready = False                 # no audio device -> stay silent
        return

    for name in EFFECT_NAMES:
        path = os.path.join(AUDIO_DIR, name + ".wav")
        if os.path.exists(path):
            try:
                _sounds[name] = pygame.mixer.Sound(path)
            except Exception:
                pass                   # skip a sound that won't load

    # Start the looping background music (-1 means "repeat forever").
    music_path = os.path.join(AUDIO_DIR, "music.wav")
    if os.path.exists(music_path):
        try:
            pygame.mixer.music.load(music_path)
            pygame.mixer.music.set_volume(MUSIC_VOLUME)
            pygame.mixer.music.play(-1)
        except Exception:
            pass


def play(name):
    """Play a one-shot sound effect by name, if sound is on."""
    if _ready and not muted and name in _sounds:
        try:
            _sounds[name].play()
        except Exception:
            pass


def toggle_mute():
    """Flip sound on/off (both effects and music). Returns the new muted state."""
    global muted
    muted = not muted
    if _ready:
        try:
            pygame.mixer.music.set_volume(0.0 if muted else MUSIC_VOLUME)
        except Exception:
            pass
    return muted
