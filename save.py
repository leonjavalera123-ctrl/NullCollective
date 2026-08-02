"""
save.py  --  remembers your progress between play sessions.
===========================================================

This is the simplest kind of "save file": we keep a few facts in a dictionary
and write them to a small text file in the JSON format. JSON looks almost exactly
like a Python dictionary, which makes it easy to read and to debug.

We only store ONE thing right now: `completed`, the number of the highest level
you've finished. From that, the menu knows whether to offer a "Continue" button
and which level it should jump to.

Everything here is wrapped in try/except so a missing or damaged save file can
never crash the game -- it just starts you fresh.
"""

import os
import json

# Put the save file right next to this code, whatever folder the game lives in.
SAVE_PATH = os.path.join(os.path.dirname(__file__), "savegame.json")

# What a brand-new player's progress looks like.
DEFAULT = {"completed": 0}      # 0 = no levels finished yet


def load():
    """Read progress from disk. Returns a dict; never raises."""
    try:
        with open(SAVE_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        # Be defensive: make sure the value is a sensible whole number 0..7.
        completed = int(data.get("completed", 0))
        completed = max(0, min(99, completed))     # clamp to a sane range
        return {"completed": completed}
    except Exception:
        # No file yet, or it was unreadable -> just start fresh.
        return dict(DEFAULT)


def save(data):
    """Write the progress dict back to disk. Never raises."""
    try:
        with open(SAVE_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)    # indent=2 keeps the file human-readable
    except Exception:
        pass                                # if saving fails, we just don't save


def reset():
    """Forget all progress (used by 'New Game')."""
    save(dict(DEFAULT))
    return dict(DEFAULT)
