"""
bossdata.py  --  every boss fight, in a form that can travel down a wire.
=========================================================================

THE PROBLEM THIS SOLVES
    Nineteen of the levels describe their boss as plain data (a quiz, or a list
    of things to flag), because they were built that way. The other nine are
    hand-written pygame screens: a password strength meter you type into, a
    cipher dial you turn, a folder of files you click. Those cannot be sent to
    the 3D office -- they ARE pygame.

    So this file gives every level a boss the office can draw, in one of two
    shapes it understands.

HOW EACH ONE IS PRODUCED, AND WHY IT MATTERS
    Where a level already holds the underlying data -- MIRAGE's inbox, GHOST's
    port scan, PLAGUE's folder, RIPPER's account list, NULL's quiz rounds -- we
    DERIVE the boss from it rather than retyping it. That keeps one source of
    truth: fix a typo in levels/level3_phishing.py and both games change.

    Only four levels needed anything written by hand, and only because their
    boss is a live interactive gadget with no list behind it: the strength
    meter, the cipher dial, the injection box and the 2FA prompt. For those we
    ask about the same understanding the gadget was testing.

THE TWO SHAPES
    quiz  {"prompt", "win", "rounds": [{"q", "options"[4], "answer" index}]}
    flag  {"prompt", "win", "scan_label", "items": [{"label","detail","bad","reason"}]}
"""


def _import(name):
    import importlib
    return importlib.import_module(name)


# ---------------------------------------------------------------------------
# DERIVED BOSSES -- built from data the levels already hold
# ---------------------------------------------------------------------------

def _mirage():
    """MIRAGE's inbox becomes a flag-the-phishing exercise."""
    L = _import("levels.level3_phishing")
    return "flag", {
        "prompt": "Triage the inbox. Flag every message that is phishing.",
        "scan_label": "Submit triage",
        "win": "You spotted the attacks. Mirage's campaign fizzles.",
        "items": [{"label": e["subject"],
                   "detail": "from " + e["sender"],
                   "bad": bool(e["phishing"]),
                   "reason": e["why"]} for e in L.EMAILS],
    }


def _ghost():
    """GHOST's port scan becomes a flag-the-backdoor exercise."""
    L = _import("levels.level4_network")
    return "flag", {
        "prompt": "Open connections on the compromised mirror. Flag the intruder.",
        "scan_label": "Kill flagged",
        "win": "Backdoor killed. Ghost is cut off.",
        "items": [{"label": "PORT %s  %s" % (p["port"], p["service"]),
                   "detail": "listening",
                   "bad": bool(p["evil"]),
                   "reason": p["note"]} for p in L.PORTS],
    }


def _plague():
    """PLAGUE's folder becomes a flag-the-malware exercise."""
    L = _import("levels.level6_malware")
    return "flag", {
        "prompt": "Quarantine the malware. Leave the safe files alone.",
        "scan_label": "Run scan",
        "win": "Perfect quarantine. Plague's payload is neutralised.",
        "items": [{"label": f.name,
                   "detail": "publisher: " + f.publisher,
                   "bad": bool(f.is_malware),
                   "reason": f.reason} for f in L.make_files()],
    }


def _ripper():
    """RIPPER's stolen database becomes a flag-the-crackable exercise."""
    L = _import("levels.level7_hashing")
    return "flag", {
        "prompt": "The stolen dump. Flag the accounts whose password will fall.",
        "scan_label": "Run cracker",
        "win": "Every crackable account found. RIPPER is countered.",
        "items": [{"label": a["user"],
                   "detail": a["hash"][:28] + "...",
                   "bad": bool(a["weak"]),
                   "reason": ("in the attacker's wordlist -- cracked instantly"
                              if a["weak"] else
                              "long and unguessable -- never cracked")}
                  for a in L.make_accounts()],
    }


def _null():
    """NULL already fights as a quiz. Take its rounds verbatim."""
    L = _import("levels.level9_null")
    return "quiz", {
        "prompt": "NULL uses every art at once. Survive the gauntlet.",
        "win": "NULL SEALED. The Collective is finished.",
        "rounds": [{"q": "%s  --  %s" % (r["skill"], r["q"]),
                    "options": list(r["options"]),
                    "answer": int(r["answer"])} for r in L.ROUNDS],
    }


# ---------------------------------------------------------------------------
# WRITTEN BOSSES -- for the four levels whose boss is a live gadget
# ---------------------------------------------------------------------------
# Each asks about exactly what the original screen made you do, so nothing is
# lost by not having the gadget itself.

_CRACKER = ("quiz", {
    "prompt": "The Cracker demands a vault password. Choose well.",
    "win": "Vault secured. The Cracker is locked out.",
    "rounds": [
        {"q": "Which of these takes longest to brute-force?",
         "options": ["P@ss1!", "correct-horse-battery-staple-92",
                     "Tr0ub4dor", "letmein2026"],
         "answer": 1},
        {"q": "Which matters MORE for resisting brute force?",
         "options": ["Adding one symbol", "Making it longer",
                     "Swapping o for 0", "Changing it monthly"],
         "answer": 1},
        {"q": "Why does 'password' fall instantly, however it is stored?",
         "options": ["It is short", "It is in every attacker's wordlist",
                     "It has no capitals", "It is an English word"],
         "answer": 1},
    ]})

_CIPHER = ("quiz", {
    "prompt": "Cipher's orders are scrambled. Prove you can read them.",
    "win": "Decrypted. The target is exposed and the bank has been warned.",
    "rounds": [
        {"q": "Decrypt this Caesar text, shift 1:  'IFMMP'",
         "options": ["HELLO", "GHOST", "WORLD", "HELPS"], "answer": 0},
        {"q": "Why is a Caesar cipher broken in seconds?",
         "options": ["The letters are visible", "There are only 25 shifts to try",
                     "It uses no computer", "It is very old"],
         "answer": 1},
        {"q": "What does % 26 do in the shift formula?",
         "options": ["Makes it faster", "Wraps Z back around to A",
                     "Removes spaces", "Picks the key"],
         "answer": 1},
    ]})

_INJECTOR = ("quiz", {
    "prompt": "You broke into the data server. Now close the hole.",
    "win": "Hole closed. The Injector's payload no longer parses as a command.",
    "rounds": [
        {"q": "Which input logs an attacker in as anybody?",
         "options": ["admin123", "' OR '1'='1", "guest", "DROP"], "answer": 1},
        {"q": "Which fix actually stops SQL injection?",
         "options": ["Tell users not to type quote marks",
                     "Use parameterised queries, so data can never be a command",
                     "Hide the error messages",
                     "Rename the database"],
         "answer": 1},
        {"q": "Why did the attack work at all?",
         "options": ["The password was weak",
                     "The site glued typed text straight into its query",
                     "The server was old", "The connection was not encrypted"],
         "answer": 1},
    ]})

_RELAY = ("quiz", {
    "prompt": "RELAY has your password and is trying to log in as you.",
    "win": "Access denied to RELAY. It had your password, but not your code.",
    "rounds": [
        {"q": "Someone claiming to be IT asks for the code on your phone. You:",
         "options": ["Read it out to be helpful", "Refuse -- real services never ask",
                     "Send only half of it", "Call back and read it out"],
         "answer": 1},
        {"q": "Why does 2FA stop an attacker who already has your password?",
         "options": ["Passwords stop working",
                     "It needs something you HAVE as well as something you KNOW",
                     "It hides your username", "It encrypts the connection"],
         "answer": 1},
        {"q": "Why does a code look like 000042 rather than 42?",
         "options": ["It is a different number",
                     "It is padded to six digits so every code is the same length",
                     "Zeroes are more secure", "The phone adds them"],
         "answer": 1},
    ]})


# Level number -> a function returning (kind, data), or a ready-made pair.
_LEGACY = {
    1: _CRACKER,
    2: _CIPHER,
    3: _mirage,
    4: _ghost,
    5: _INJECTOR,
    6: _plague,
    26: _ripper,
    27: _RELAY,
    28: _null,
}


def boss_for(level):
    """Return {"kind": "quiz"|"flag", "data": {...}} or None if there's no boss.

    Boot camps have no boss on purpose -- they are a lesson and a lab, and
    ending them with a test would undo the point of them.
    """
    import bootcamp
    if level in bootcamp.EXTRA_MODULES:
        return None

    if level in _LEGACY:
        entry = _LEGACY[level]
        kind, data = entry() if callable(entry) else entry
        return {"kind": kind, "data": data}

    # Everything else is a data level, which already carries its own boss.
    import datalevels
    idx = level - 7                      # levels 7.. map onto DATA_LEVELS[0..]
    if 0 <= idx < len(datalevels.DATA_LEVELS):
        d = datalevels.DATA_LEVELS[idx]
        return {"kind": d["boss_kind"], "data": d["boss_data"]}
    return None
