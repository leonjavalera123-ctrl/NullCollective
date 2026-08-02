"""
LEVEL 7  --  RIPPER   (Password hashing & how databases get cracked)
====================================================================

Security idea you learn:
    Good websites never store your real password. They store a "hash" -- a
    one-way scramble produced by a function like SHA-256. You can hash a value
    in an instant, but you can't un-hash it back. So how do attackers crack
    stolen databases? They hash millions of GUESSES and look for a matching
    hash. Weak passwords match a guess fast; strong ones never do.

Python you learn:
    - using a real library: import hashlib
    - calling library functions: hashlib.sha256(text.encode()).hexdigest()
    - that the same input ALWAYS gives the same hash (and a tiny change gives a
      totally different one)
    - writing your own hashing helper and a hash-cracking loop

How the level plays:
    RIPPER stole a password database. You'll inspect the hashes and flag which
    accounts used a crackable (common) password, then run the cracker to prove it.
"""

import hashlib
import pygame
from engine import Scene, Button, draw_text, COLORS, WIDTH, HEIGHT


def sha(text):
    """Return the SHA-256 hash of some text as a hex string. (A tiny helper.)"""
    return hashlib.sha256(text.encode()).hexdigest()


# The attacker's wordlist of very common passwords.
COMMON = ["123456", "password", "qwerty", "letmein", "sunshine",
          "football", "dragon", "monkey"]


# ===========================================================================
# INTEL
# ===========================================================================
INTEL = [
    {"heading": "What RIPPER does",
     "body": "RIPPER steals databases full of password HASHES and cracks them. "
             "The attack is simple: hash every word in a wordlist and compare each "
             "result to the stolen hashes. A match reveals the real password. This "
             "is how 'cracked' password dumps happen.",
     "code": "for guess in wordlist:\n"
             "    if sha256(guess) == stolen_hash:\n"
             "        print('CRACKED:', guess)"},
    {"heading": "Why hashing helps (and where it fails)",
     "body": "A hash is one-way: easy to compute, practically impossible to "
             "reverse. That protects strong passwords. But if your password is a "
             "common word, the attacker's wordlist contains it -- so its hash is "
             "matched almost instantly. Length and unpredictability are everything.",
     "code": "sha256('password') -> 5e884898da...  (in every wordlist)\n"
             "sha256('7$kQ9_wZ!mLp2') -> never guessed"},
    {"heading": "Real scenario",
     "body": "When big sites are breached, it's the hashes that leak. Within hours, "
             "tools hash billions of common guesses and crack every weak password. "
             "In the lab you'll hash text yourself with Python's real hashlib "
             "library, then write the cracking loop.",
     "code": None},
]


# ===========================================================================
# CHALLENGES
# ===========================================================================
def _check_h(t):
    return t.ns.get("h") == sha("hello")

def _check_avalanche(t):
    return t.ns.get("h2") == sha("Hello")

def _check_myhash(t):
    f = t.ns.get("myhash")
    if not callable(f):
        return False
    try:
        return f("abc") == sha("abc") and f("xyz") == sha("xyz")
    except Exception:
        return False

def _check_cracked(t):
    return t.ns.get("cracked") == "letmein"

def _check_reused(t):
    return t.ns.get("reused") is True

CHALLENGES = [
    {"title": "Make a hash",
     "goal": "`hashlib` is Python's real hashing library (already loaded for you). "
             "Hash the word 'hello' and store the result in `h`. The recipe is: "
             "hashlib.sha256(\"hello\".encode()).hexdigest()",
     "seed": lambda: {"hashlib": hashlib},
     "intro": ["# `hashlib` is ready. .encode() prepares text for hashing;",
               "# .hexdigest() gives the hash as readable text.",
               "# Store the hash of 'hello' in `h`, then type  h  to see it."],
     "hint": "h = hashlib.sha256(\"hello\".encode()).hexdigest()",
     "solution": "h = hashlib.sha256(\"hello\".encode()).hexdigest()",
     "check": _check_h,
     "success": "That long string IS the hash of 'hello' -- and it's always the same."},
    {"title": "Tiny change, huge difference",
     "goal": "Now hash 'Hello' (capital H) into `h2`. Compare it to `h` -- a single "
             "changed letter produces a COMPLETELY different hash. That's what makes "
             "hashing useful.",
     "seed": lambda: {"hashlib": hashlib},
     "intro": ["# Hash 'Hello' (capital H) into h2.",
               "# Notice how different it is from the lowercase version."],
     "hint": "h2 = hashlib.sha256(\"Hello\".encode()).hexdigest()",
     "solution": "h2 = hashlib.sha256(\"Hello\".encode()).hexdigest()",
     "check": _check_avalanche,
     "success": "One capital letter changed everything. This is called the avalanche effect."},
    {"title": "Write a hasher",
     "goal": "Write a function `myhash(text)` that returns the SHA-256 hex hash of "
             "`text`. It just wraps the recipe you used above so you can reuse it.",
     "seed": lambda: {"hashlib": hashlib},
     "intro": ["# def myhash(text):  return the sha256 hexdigest of text.",
               "# Test:  myhash('abc')  should give a long hex string."],
     "hint": "def myhash(text):  return hashlib.sha256(text.encode()).hexdigest()",
     "solution": "def myhash(text):\n    return hashlib.sha256(text.encode()).hexdigest()",
     "check": _check_myhash,
     "success": "A reusable hasher -- the same tool both defenders and attackers use."},
    {"title": "Crack a stolen hash",
     "goal": "`stolen` is a hash from RIPPER's loot and `wordlist` holds guesses. "
             "Loop through the wordlist, hash each guess, and when it matches "
             "`stolen`, store that guess in `cracked`.",
     "seed": lambda: {"hashlib": hashlib,
                      "wordlist": ["apple", "letmein", "banana", "sunshine"],
                      "stolen": sha("letmein")},
     "intro": ["# `stolen` is a sha256 hash. `wordlist` holds candidate passwords.",
               "# Hash each guess and compare to `stolen`; save the match in `cracked`.",
               "# Hash a guess with:  hashlib.sha256(guess.encode()).hexdigest()"],
     "hint": "for g in wordlist:  /  if hashlib.sha256(g.encode()).hexdigest() == stolen:  /  cracked = g",
     "solution": "for g in wordlist:\n    if hashlib.sha256(g.encode()).hexdigest() == stolen:\n"
                 "        cracked = g",
     "check": _check_cracked,
     "success": "Cracked! A weak password's hash falls to a wordlist in moments."},
    {"title": "Spot a reused password",
     "goal": "Plain hashing has a weakness: identical passwords make identical "
             "hashes. Set `reused` to True if `hash_a` and `hash_b` are equal -- "
             "which would reveal two people share a password.",
     "seed": lambda: {"hash_a": sha("hunter2"), "hash_b": sha("hunter2")},
     "intro": ["# `hash_a` and `hash_b` are two stored password hashes.",
               "# Are they the same?  Set `reused` to the True/False answer."],
     "hint": "reused = hash_a == hash_b",
     "solution": "reused = hash_a == hash_b",
     "check": _check_reused,
     "success": "Equal hashes = same password. (Real sites add a 'salt' to prevent this.)"},
]


# ===========================================================================
# BOSS FIGHT  --  inspect RIPPER's stolen database and flag the weak accounts.
# ===========================================================================
def make_accounts():
    data = [
        ("alice", "password",       True),
        ("bob",   "Tr0ub4dor&3xKp", False),
        ("carol", "qwerty",         True),
        ("dave",  "7$kQ9_wZ!mLp2",  False),
        ("erin",  "letmein",        True),
    ]
    accounts = []
    for user, pw, weak in data:
        accounts.append({"user": user, "pw": pw, "hash": sha(pw),
                         "weak": weak, "flagged": False})
    return accounts


class Level7(Scene):
    def __init__(self, game):
        super().__init__(game)
        self.accounts = make_accounts()
        self.row_rects = []
        self.cracked = False           # has the player run the cracker yet?
        self.won = False
        self.message = ("Flag the accounts whose password looks crackable, then run "
                        "the cracker.")
        self.scan_btn = Button(60, HEIGHT - 90, 240, 56, "Run Cracker", color="amber")
        self.continue_btn = Button(WIDTH - 240, HEIGHT - 90, 200, 56, "Continue >")

    def crack(self):
        """Actually hash every common password and compare -- the real attack."""
        self.cracked = True
        wrong = 0
        for acc in self.accounts:
            # An account is crackable if its hash matches some common password.
            crackable = any(sha(c) == acc["hash"] for c in COMMON)
            acc["found"] = next((c for c in COMMON if sha(c) == acc["hash"]), None)
            if acc["flagged"] != crackable:
                wrong += 1
        if wrong == 0:
            self.won = True
            self.message = "Correct! You spotted every crackable account. RIPPER is countered."
        else:
            self.message = f"{wrong} wrong. Review the cracked passwords and try again."

    def handle_event(self, event):
        if self.won:
            if self.continue_btn.handle_event(event):
                self.next_scene = self.return_to
            return
        if self.scan_btn.handle_event(event):
            self.crack()
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for i, rect in enumerate(self.row_rects):
                if rect.collidepoint(event.pos):
                    self.accounts[i]["flagged"] = not self.accounts[i]["flagged"]

    def draw(self, surface):
        surface.fill(COLORS["bg"])
        self.draw_header(surface, "LEVEL 7  //  RIPPER")
        draw_text(surface, self.message, 60, 88, size=19,
                  color="green" if self.won else "amber", max_width=WIDTH - 120)

        self.row_rects = []
        y = 130
        for i, acc in enumerate(self.accounts):
            rect = pygame.Rect(60, y, WIDTH - 120, 64)
            self.row_rects.append(rect)
            if self.cracked and acc["weak"]:
                bg = COLORS["red"] if acc["flagged"] else COLORS["panel2"]
            elif acc["flagged"]:
                bg = (70, 30, 30)
            else:
                bg = COLORS["panel"]
            pygame.draw.rect(surface, bg, rect, border_radius=8)
            pygame.draw.rect(surface, COLORS["gray"], rect, width=1, border_radius=8)
            mark = "[AT RISK]" if acc["flagged"] else "[       ]"
            draw_text(surface, mark, 76, y + 8, size=17,
                      color="red" if acc["flagged"] else "gray")
            draw_text(surface, acc["user"], 250, y + 8, size=20, color="white")
            # Show a shortened hash so the row isn't a mile wide.
            draw_text(surface, acc["hash"][:32] + "...", 360, y + 11, size=15,
                      color="cyan")
            if self.cracked:
                if acc.get("found"):
                    draw_text(surface, f"CRACKED -> \"{acc['found']}\"", 360, y + 38,
                              size=15, color="red")
                else:
                    draw_text(surface, "not in wordlist -- strong password", 360, y + 38,
                              size=15, color="green")
            y += 72

        if self.won:
            self.continue_btn.draw(surface)
        else:
            self.scan_btn.draw(surface)
