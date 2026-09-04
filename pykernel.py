"""
pykernel.py  --  the Python brain of the game, with no game attached.
=====================================================================

This is the part of NULL Collective that actually RUNS your code, lifted out so
it can work on its own. The pygame version of the lab (pyterminal.py + LabScene)
draws a terminal AND runs the code AND tracks how much help you needed. This file
does only the last two.

WHY IT EXISTS
    The 3D office wants to put a terminal on the monitor in front of you, instead
    of opening a second window. Godot can't run Python -- so Godot draws the
    terminal, and this runs behind it and sends the answers back.

WHAT IT DELIBERATELY DOESN'T DO
    No pygame, no drawing, no sound, no input handling. Give it a line of code,
    get back the lines of output. That is the whole contract, and it's why the
    same file can serve a pygame window, a socket, or a test.

THE ONE THING THAT MAKES THIS WORK AT ALL
    Every level's `check(t)` function was written to take the pygame terminal and
    look at exactly two things: `t.ns` (the variables you've made) and
    `t.last_run` (what your last command printed). Nothing else. So `Kernel` just
    provides those two attributes and all 65 existing checkers run untouched --
    no rewrites, no duplicated answer logic, no chance of the two games
    disagreeing about whether you solved something.
"""

import io
import os
import copy
import contextlib

# The level content lives in the pygame game's modules. Importing them pulls in
# pygame, so we point SDL at a dummy driver first: that lets pygame load with no
# window, no sound card and no display of any kind.
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import handoff        # for is_clean(), so "clean" means one thing everywhere


def _load_campaign():
    """Fetch the level list lazily, so importing this file stays cheap."""
    import main
    import bootcamp
    return main, bootcamp


def challenges_for(level):
    """The lab tasks for a level.

    The boot camps live in bootcamp.EXTRA_MODULES rather than in the campaign,
    so we look there first. Everything else is a campaign mission, numbered from
    1. Checking the table first means adding another optional module needs no
    changes here at all.
    """
    main, bootcamp = _load_campaign()
    if level in bootcamp.EXTRA_MODULES:
        return bootcamp.EXTRA_MODULES[level]["challenges"]
    if 1 <= level <= len(main.CAMPAIGN):
        return main.CAMPAIGN[level - 1]["challenges"]
    return []


def level_title(level):
    main, bootcamp = _load_campaign()
    if level in bootcamp.EXTRA_MODULES:
        return bootcamp.EXTRA_MODULES[level]["title"]
    if 1 <= level <= len(main.CAMPAIGN):
        return main.CAMPAIGN[level - 1]["boss"]
    return "MODULE %d" % level


def briefing_for(level):
    """The teaching material that comes BEFORE the lab.

    Every level already carries three things written to be read in order:
        brief   -- the mission, in one paragraph
        intel   -- what the attacker actually does, with their real code
        lesson  -- the Python you'll need, taught slowly, one idea per card

    The pygame game always showed these. The first version of the embedded
    terminal did not, and dropped the player straight into the challenges with
    no idea what they were looking at -- which is exactly as unfair as it sounds.
    """
    main, bootcamp = _load_campaign()
    if level in bootcamp.EXTRA_MODULES:
        # Boot camps have no villain, so no intel section -- just the teaching.
        m = bootcamp.EXTRA_MODULES[level]
        return {"brief": m["brief"], "intel": [], "lesson": list(m["lesson"])}
    if 1 <= level <= len(main.CAMPAIGN):
        prov = main.CAMPAIGN[level - 1]
        return {
            "brief": prov.get("brief", ""),
            "intel": list(prov.get("intel", [])),
            "lesson": list(prov.get("lesson", [])),
        }
    return {"brief": "", "intel": [], "lesson": []}


# ---------------------------------------------------------------------------
# THE KERNEL -- runs one line of Python and says what happened
# ---------------------------------------------------------------------------
class Kernel:
    """Runs code in a namespace and reports the output.

    It carries exactly the two attributes the level checkers expect:
        .ns        the dictionary of variables you've created
        .last_run  the text your most recent command produced
    """

    def __init__(self, seed=None):
        self.ns = {}
        self.last_run = ""
        self.block = []            # lines of a partly-typed for/if/def
        self.reset(seed)

    def reset(self, seed=None):
        """Wipe the namespace and load a challenge's starting data."""
        self.ns = {}
        if seed:
            try:
                self.ns.update(copy.deepcopy(seed))
            except Exception:
                self.ns.update(dict(seed))
        self.last_run = ""
        self.block = []

    # -- the part lifted from pyterminal.run_source ------------------------
    def run_source(self, source):
        """Compile and run a complete piece of code.

        Returns a list of [text, colour] pairs to print. Colours are names the
        Godot side understands: white, cyan, red.
        """
        lines = []
        self.last_run = ""
        buffer = io.StringIO()
        try:
            # Try it as an EXPRESSION first (something with a value, like 2+2),
            # and fall back to STATEMENTS (something that does a thing).
            try:
                code = compile(source, "<lab>", "eval")
                is_expr = True
            except SyntaxError:
                code = compile(source, "<lab>", "exec")
                is_expr = False

            # Anything the player print()s goes into our buffer, not the console.
            with contextlib.redirect_stdout(buffer):
                if is_expr:
                    result = eval(code, self.ns)
                else:
                    exec(code, self.ns)
                    result = None

            printed = buffer.getvalue()
            if printed:
                for ln in printed.rstrip("\n").split("\n"):
                    lines.append([ln, "white"])
            # A bare expression shows its value, exactly like the real prompt.
            if is_expr and result is not None:
                lines.append([repr(result), "cyan"])
            self.last_run = printed + ("" if result is None else repr(result))

        except Exception as e:
            # Show the error type and message. Reading these is a skill, so we
            # keep them short and never hide them.
            msg = "%s: %s" % (type(e).__name__, e)
            lines.append([msg, "red"])
            self.last_run = msg
        return lines

    def submit(self, line):
        """Handle one typed line, exactly like the pygame terminal does.

        A line ending in ':' starts a multi-line block; you keep typing, and a
        blank line runs the whole thing. Returns (lines, in_block).
        """
        out = []
        prompt = "... " if self.block else ">>> "
        out.append([prompt + line, "green"])

        if self.block:
            if line.strip() == "":
                source = "\n".join(self.block)
                self.block = []
                out.extend(self.run_source(source))
            else:
                self.block.append(line)
        else:
            if line.strip() == "":
                pass
            elif line.rstrip().endswith(":"):
                self.block.append(line)
            else:
                out.extend(self.run_source(line))
        return out, bool(self.block)


# ---------------------------------------------------------------------------
# A SESSION -- one level's worth of lab, with the same scoring as LabScene
# ---------------------------------------------------------------------------
class Session:
    """Walks a player through one level's challenges and tallies the help used.

    This mirrors labscene.py's logic on purpose: latch a hint the first time it's
    opened, count a skip when you leave a challenge unsolved, and never let the
    two games disagree about what happened.
    """

    def __init__(self, level):
        self.level = level
        self.title = level_title(level)
        self.challenges = list(challenges_for(level))
        self.idx = 0
        self.solved = False

        # --- the boss fight ------------------------------------------------
        # A mission is the lab AND the boss. The lab teaches the Python; the
        # boss makes you use the judgement it taught. `phase` says where we are.
        import bossdata
        self.boss = bossdata.boss_for(level)      # None for the boot camps
        self.boss_round = 0
        self.boss_misses = 0
        self.boss_won = False
        self.phase = "lab" if self.challenges else (
            "boss" if self.boss else "done")
        self.done = self.phase == "done"
        self.stats = {
            "challenges": len(self.challenges),
            "solved": 0, "hints": 0, "solutions": 0, "skips": 0,
        }
        self._hint_counted = False
        self._solution_counted = False
        self.term = Kernel()
        if not self.done:
            self._begin()

    # -- challenge lifecycle ----------------------------------------------
    def _begin(self):
        ch = self.challenges[self.idx]
        seed = ch.get("seed")
        if callable(seed):
            seed = seed()
        self.term.reset(seed)
        self.solved = False
        self._hint_counted = False
        self._solution_counted = False

    def current(self):
        """Everything Godot needs to draw the current challenge.

        Returns None unless we are actually IN the lab. Checking `done` alone
        was not enough once the boss arrived: during the boss phase `done` is
        still False but `idx` has already run off the end of the list, so this
        raised IndexError and the whole request failed.
        """
        if self.phase != "lab" or self.idx >= len(self.challenges):
            return None
        ch = self.challenges[self.idx]
        return {
            "index": self.idx,
            "count": len(self.challenges),
            "title": ch.get("title", ""),
            "goal": ch.get("goal", ""),
            "intro": list(ch.get("intro", [])),
            "hint": ch.get("hint", ""),
            "solution": ch.get("solution", ""),
            "success": ch.get("success", ""),
        }

    def _check(self):
        """Ask this challenge's own checker whether it's been solved.

        `self.term` is handed straight in as the `t` argument -- the same shape
        the pygame terminal has, which is why these functions need no changes.
        """
        if self.solved or self.done:
            return self.solved
        fn = self.challenges[self.idx].get("check")
        if not fn:
            return False
        try:
            if fn(self.term):
                self.solved = True
        except Exception:
            pass          # a half-typed attempt can raise; that's not a failure
        return self.solved

    # -- what Godot calls --------------------------------------------------
    def submit(self, line):
        lines, in_block = self.term.submit(line)
        return {"lines": lines, "in_block": in_block, "solved": self._check()}

    def mark_hint(self):
        if not self._hint_counted:
            self.stats["hints"] += 1
            self._hint_counted = True

    def mark_solution(self):
        if not self._solution_counted:
            self.stats["solutions"] += 1
            self._solution_counted = True

    def advance(self):
        """Leave the current challenge, scoring it on the way out."""
        if self.phase != "lab":
            return
        if self.solved:
            self.stats["solved"] += 1
        else:
            self.stats["skips"] += 1
        self.idx += 1
        if self.idx >= len(self.challenges):
            # Lab finished. The mission isn't over: the boss is next.
            self.phase = "boss" if self.boss else "done"
            self.done = self.phase == "done"
        else:
            self._begin()

    # -- the boss fight ----------------------------------------------------
    def boss_spec(self):
        """What the office needs to draw the boss, with the answers stripped.

        The correct answers stay HERE. Sending them would let anyone read the
        solution straight off the wire, which rather defeats the exercise.
        """
        # Only describe the boss while we are actually fighting it. Once it is
        # beaten, boss_round has run past the last question -- reading it would
        # raise IndexError, exactly as current() did during the boss phase.
        if not self.boss or self.phase != "boss":
            return None
        kind, data = self.boss["kind"], self.boss["data"]
        if kind == "quiz":
            if self.boss_round >= len(data["rounds"]):
                return None
            r = data["rounds"][self.boss_round]
            return {"kind": "quiz",
                    "prompt": data.get("prompt", ""),
                    "round": self.boss_round,
                    "count": len(data["rounds"]),
                    "q": r["q"],
                    "options": list(r["options"])}
        return {"kind": "flag",
                "prompt": data.get("prompt", ""),
                "scan_label": data.get("scan_label", "Run scan"),
                "items": [{"label": i["label"], "detail": i.get("detail", "")}
                          for i in data["items"]]}

    def boss_answer(self, payload):
        """Judge one boss answer. Returns what happened, in plain fields."""
        if self.phase != "boss" or not self.boss:
            return {"win": self.boss_won}
        kind, data = self.boss["kind"], self.boss["data"]

        if kind == "quiz":
            r = data["rounds"][self.boss_round]
            correct = int(payload.get("choice", -1)) == int(r["answer"])
            if correct:
                self.boss_round += 1
                if self.boss_round >= len(data["rounds"]):
                    self.boss_won = True
                    self.phase = "done"
                    self.done = True
            else:
                self.boss_misses += 1
            return {"correct": correct, "win": self.boss_won,
                    "misses": self.boss_misses,
                    "message": ("Correct." if correct
                                else "Not quite -- think it through and try again.")}

        # flag: you submit your whole judgement at once
        flags = list(payload.get("flags", []))
        items = data["items"]
        wrong = []
        for i, item in enumerate(items):
            said = bool(flags[i]) if i < len(flags) else False
            if said != bool(item["bad"]):
                wrong.append(i)
        if not wrong:
            self.boss_won = True
            self.phase = "done"
            self.done = True
            return {"correct": True, "win": True, "misses": self.boss_misses,
                    "message": data.get("win", "All threats identified."),
                    # On a win we reveal every reason, because that's the
                    # teaching: WHY each one was or wasn't a threat.
                    "reasons": [i.get("reason", "") for i in items]}
        self.boss_misses += 1
        return {"correct": False, "win": False, "misses": self.boss_misses,
                "wrong": wrong,
                "message": "%d judged wrongly. Look again at the highlighted rows."
                           % len(wrong)}

    def report(self, session_id, asked_level):
        """The same shape the launcher path writes, so the office can't tell
        which route produced it."""
        # A mission counts as CLEARED when the whole thing is done -- lab AND
        # boss. A level with no boss (the boot camps) clears on the lab alone.
        cleared = bool(self.done) and (self.boss_won or self.boss is None)
        r = {
            "session_id": session_id,
            "asked_level": asked_level,
            "finished_level": self.level if cleared else None,
            "cleared": cleared,
            "boss_misses": self.boss_misses,
            "challenges": self.stats["challenges"],
            "solved": self.stats["solved"],
            "hints_shown": self.stats["hints"],
            "solutions_shown": self.stats["solutions"],
            "skips": self.stats["skips"],
        }
        # One source of truth for "clean" -- the same function the pygame side
        # uses, so the two paths can never grade differently.
        r["clean"] = handoff.is_clean(r)
        return r
