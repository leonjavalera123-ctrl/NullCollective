"""
handoff.py  --  lets the 3D office game ask this game to run ONE mission.
=========================================================================

Read this if you're wondering how two separate games talk to each other.

THE PROBLEM
    The 3D office (built in Godot) can't run Python. So when you walk up to a
    terminal and press E, the office launches THIS game as a separate program.
    But it needs to say two things:
        "run level 3, please"   ... and later ...   "so, how did it go?"

THE SOLUTION -- two one-way messages, both dead simple:

    1) The office ASKS by passing command-line arguments when it starts us:

           python main.py --level 3 --session abc123 --report C:/tmp/r.json

       `read_request()` below reads those. If there are none (you just
       double-clicked the game normally), it returns None and NOTHING changes --
       the game boots to its usual title menu.

    2) We ANSWER by writing a small JSON file at the path we were given.
       `write_report()` below does that. The office reads it and closes the ticket.

WHY COMMAND-LINE ARGUMENTS AND NOT A SHARED FILE?
    A leftover "please run level 3" file would silently hijack the game the next
    time you opened it normally. Arguments vanish when the program closes, so
    they can never go stale.

WHY THE SESSION ID?
    So an OLD report file can never be mistaken for this run. The office makes up
    an id, we echo it back, and the office ignores any report that doesn't match.

This file imports nothing from the rest of the game, so it can never break it.
"""

import os
import sys
import json


def read_request(argv=None):
    """Look at the command line for a request from the office.

    Returns a dictionary like:
        {"level": 3, "session": "abc123", "report": "C:/tmp/r.json"}
    or None if no level was requested -- which means "just start normally".

    `argv` is only passed in by tests; normally we read the real command line.
    """
    # sys.argv[0] is the script name itself, so we skip it with [1:].
    args = sys.argv[1:] if argv is None else list(argv)

    level = None
    session = ""
    report = ""

    i = 0
    while i < len(args):
        word = args[i]
        # Each flag is followed by its value, so we look one step ahead.
        has_value = (i + 1) < len(args)

        if word == "--level" and has_value:
            try:
                level = int(args[i + 1])
            except ValueError:
                level = None          # not a number -> treat as no request
            i += 2
        elif word == "--session" and has_value:
            session = args[i + 1]
            i += 2
        elif word == "--report" and has_value:
            report = args[i + 1]
            i += 2
        else:
            i += 1                    # something we don't recognise -- ignore it

    if level is None:
        return None                   # no level asked for -> normal startup

    return {"level": level, "session": session, "report": report}


def is_clean(report):
    """Did the player solve this mission under their own steam?

    CLEAN means: every challenge was solved, nothing was skipped, and the
    answer was never revealed.

    HINTS ARE FREE ON PURPOSE. A nervous beginner should be able to lean on
    hints as much as they like and still earn full marks -- the thing we're
    actually measuring is "did you get there yourself", and a nudge in the right
    direction still counts as getting there. Only *reading the answer* or
    *skipping* means the challenge didn't teach you anything.

    Anything missing or malformed grades as NOT clean. That matters: if a
    session crashes before it can report, we must never award a better result
    than the player earned.
    """
    if not isinstance(report, dict):
        return False

    def count(key):
        try:
            return int(report.get(key, 0) or 0)
        except (TypeError, ValueError):
            return 0

    if not report.get("cleared", False):
        return False                 # didn't finish the mission at all
    if count("challenges") <= 0:
        return False                 # no lab data -> can't claim anything
    if count("skips") > 0:
        return False
    if count("solutions_shown") > 0:
        return False
    return True


def write_report(path, data):
    """Write the results back to the office, safely.

    THE SUBTLE BIT: the office might read this file at the exact moment we're
    writing it, and would then see half a file and crash. So we write to a
    TEMPORARY name first, then rename it into place. On every modern operating
    system that rename is "atomic" -- it happens all at once, so the office
    either sees the old file or the complete new one, never something in between.

    Never raises. A failure to report should not crash the game you're playing.
    """
    if not path:
        return False                  # nobody asked for a report

    try:
        folder = os.path.dirname(os.path.abspath(path))
        if folder:
            os.makedirs(folder, exist_ok=True)   # make sure the folder exists

        temp_path = path + ".tmp"
        with open(temp_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

        os.replace(temp_path, path)   # <- the atomic swap
        return True
    except Exception:
        return False                  # silently give up; the game keeps working
