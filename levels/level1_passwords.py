"""
LEVEL 1  --  THE CRACKER   (Passwords & brute-force)
====================================================

Security idea you learn:
    "Brute-forcing" means an attacker tries password after password until one
    works. Computers do this billions of times per second. A short, simple
    password falls in moments; a long one could take longer than your lifetime.

Python you learn:
    - variables and strings
    - if / elif / else decisions
    - looping over the characters of a string
    - string methods like .isdigit(), .isupper(), .islower()
    - building a score by adding to a number

How the level plays:
    You type a password into the box. A live meter rates it and estimates how
    long The Cracker would need to brute-force it. Reach "STRONG" to win.
"""

import pygame
from engine import Scene, Button, TextInput, draw_text, COLORS, WIDTH, HEIGHT


# ===========================================================================
# INTEL  --  what The Cracker (the enemy hacker) actually does.
# Each section is shown on its own page before you reach the lab.
# ===========================================================================
INTEL = [
    {
        "heading": "What The Cracker does",
        "body": "The Cracker runs a 'brute-force' attack: a program that simply "
                "tries password after password until one works. No magic -- just "
                "a loop and a comparison, repeated billions of times a second. "
                "Here is the entire idea in real Python:",
        "code": "for guess in wordlist:\n"
                "    if guess == real_password:\n"
                "        print('CRACKED:', guess)\n"
                "        break",
    },
    {
        "heading": "Why weak passwords fall instantly",
        "body": "Attackers start with a 'wordlist' of the most common passwords "
                "(a 'dictionary attack'). If your password is on that list, it's "
                "found on the very first pass. Only when a password is long and "
                "unpredictable does the loop have too many combinations to ever "
                "finish. That number is pool_of_characters raised to the length:",
        "code": "combinations = pool ** length   # ** means 'to the power of'\n"
                "# 8 lowercase letters  -> 26**8  = 208 billion\n"
                "# 16 mixed characters  -> 94**16 = effectively unbreakable",
    },
    {
        "heading": "Real scenario",
        "body": "In 2012, attackers stole 6.5 million LinkedIn password hashes. "
                "Because so many were short and common, most were cracked within "
                "days using exactly the loop above. The lesson you'll practice in "
                "the lab: write the attack yourself, so you understand the defense.",
        "code": None,
    },
]


# ===========================================================================
# CHALLENGES  --  the hands-on Python you type in the in-game terminal.
# Each `check` function receives the live terminal `t`, so it can read the
# variables you made (t.ns) and the text your last command printed (t.last_run).
# ===========================================================================
def _check_secret(t):
    # Pass when a variable `secret` exists and is a string of length >= 12.
    secret = t.ns.get("secret")
    return isinstance(secret, str) and len(secret) >= 12

def _check_printed_all(t):
    # Pass when the last command printed every word in the wordlist.
    words = ["123456", "password", "qwerty", "letmein", "dragon"]
    return all(w in t.last_run for w in words)

def _check_found(t):
    # Pass when the player's loop stored the matching password in `found`.
    return t.ns.get("found") == "letmein"

def _check_length(t):
    return t.ns.get("length") == 8

def _check_long_enough(t):
    return t.ns.get("strong_enough") is False

CHALLENGES = [
    {
        "title": "Make a variable",
        "goal": "A variable is a labeled box that stores a value. Create one named "
                "`secret` holding a strong password at least 12 characters long. "
                "Example to type:   secret = \"my-long-passphrase\"",
        "intro": ["# Goal: define `secret` = a string of 12+ characters."],
        "hint": "Type:  secret = \"correct-horse-battery\"  then press Enter. "
                "Then type  len(secret)  to see its length.",
        "solution": 'secret = "correct-horse-battery-92"',
        "check": _check_secret,
        "success": "That's a variable holding a string. len(secret) would beat the dictionary attack.",
    },
    {
        "title": "Measure the password",
        "goal": "len() counts how many characters are in a string. Store the length "
                "of `password` in a variable named `length`.",
        "seed": lambda: {"password": "sunshine"},
        "intro": ["# `password` is preloaded. Try:  len(password)",
                  "# Then store that number in a variable called `length`."],
        "hint": "length = len(password)",
        "solution": "length = len(password)",
        "check": _check_length,
        "success": "len(password) is 8. Now you can measure any password's length.",
    },
    {
        "title": "Is it long enough?",
        "goal": "A comparison gives back True or False. Set `strong_enough` to "
                "whether `password` has 12 or more characters, using the "
                "comparison  len(password) >= 12.",
        "seed": lambda: {"password": "sunshine"},
        "intro": ["# `password` = 'sunshine' (8 letters).",
                  "# Is it 12+ characters?  len(password) >= 12  is True or False."],
        "hint": "strong_enough = len(password) >= 12",
        "solution": "strong_enough = len(password) >= 12",
        "check": _check_long_enough,
        "success": "'sunshine' is only 8 chars, so strong_enough is False. That's a boolean.",
    },
    {
        "title": "Loop like a cracker",
        "goal": "The list `wordlist` holds 5 common passwords. Use a for-loop to "
                "print each one (that's the attacker's first move). Type the first "
                "line, press Enter, type the indented line, then Enter on a BLANK "
                "line to run the block.",
        "seed": lambda: {"wordlist": ["123456", "password", "qwerty",
                                       "letmein", "dragon"]},
        "intro": ["# `wordlist` is preloaded with 5 common passwords.",
                  "# Loop over it and print() each one."],
        "hint": "for word in wordlist:  (Enter)  then  >    print(word)  (Enter, Enter)",
        "solution": "for word in wordlist:\n    print(word)",
        "check": _check_printed_all,
        "success": "You just ran a dictionary attack's core loop.",
    },
    {
        "title": "Crack it",
        "goal": "`wordlist` holds passwords and `target` is the real one. Write a "
                "loop with an `if` that finds the match and stores it in a variable "
                "named `found`. (The real password is somewhere in the list.)",
        "seed": lambda: {"wordlist": ["123456", "password", "qwerty",
                                       "letmein", "dragon"],
                         "target": "letmein"},
        "intro": ["# `wordlist` = list of guesses, `target` = the real password.",
                  "# Loop, compare each guess to target, save the winner in `found`."],
        "hint": "for w in wordlist:  /  if w == target:  /  found = w",
        "solution": "for w in wordlist:\n    if w == target:\n        found = w",
        "check": _check_found,
        "success": "Cracked! That if-inside-a-loop is exactly how brute-force works.",
    },
]


# A set of symbol characters we'll check for. A "set" (curly braces) is great for
# fast "is this character one of these?" questions.
SYMBOLS = set("!@#$%^&*()-_=+[]{};:,.<>?/|")


def rate_password(pw):
    """Look at a password string and return (score, list_of_feedback_messages).

    This is a plain function -- give it a string, get back a number and some tips.
    We build the score by checking one quality at a time and adding points.
    """
    score = 0
    tips = []

    # --- Quality 1: length. Each rule is a simple if-statement. ---
    if len(pw) >= 12:
        score += 3
    elif len(pw) >= 8:
        score += 2
        tips.append("Make it 12+ characters -- length matters most.")
    elif len(pw) >= 1:
        score += 1
        tips.append("Too short. Aim for at least 12 characters.")

    # --- Quality 2: variety. We loop through every character ONCE and note ---
    # --- which "families" appear. These start False and flip to True if found. ---
    has_lower = False
    has_upper = False
    has_digit = False
    has_symbol = False
    for ch in pw:                 # `ch` becomes each character in turn
        if ch.islower():
            has_lower = True
        elif ch.isupper():
            has_upper = True
        elif ch.isdigit():
            has_digit = True
        elif ch in SYMBOLS:
            has_symbol = True

    # Add a point for each family present, and a tip for each one missing.
    if has_lower:
        score += 1
    if has_upper:
        score += 1
    else:
        tips.append("Add an UPPERCASE letter.")
    if has_digit:
        score += 1
    else:
        tips.append("Add a digit (0-9).")
    if has_symbol:
        score += 1
    else:
        tips.append("Add a symbol like ! or #.")

    # --- Quality 3: penalize obvious passwords. ---
    common = ("password", "123456", "qwerty", "admin", "letmein", "null")
    if pw.lower() in common:
        score = 0
        tips = ["That's one of the most common passwords on Earth. NULL guessed it instantly."]

    return score, tips


def pool_size(pw):
    """Estimate how many DIFFERENT characters an attacker must consider.

    If your password uses lowercase only, the attacker tries 26 options per slot.
    Add uppercase -> 52, digits -> 62, symbols -> ~94. A bigger pool + more slots
    means astronomically more combinations to brute-force.
    """
    pool = 0
    if any(c.islower() for c in pw):       # any() is True if ANY char is lowercase
        pool += 26
    if any(c.isupper() for c in pw):
        pool += 26
    if any(c.isdigit() for c in pw):
        pool += 10
    if any(c in SYMBOLS for c in pw):
        pool += 32
    return pool


def crack_time_text(pw):
    """Return a friendly 'time to crack' estimate as a string.

    The math: combinations = pool ** length  (** means "to the power of").
    We assume a fast attacker guessing 10 billion passwords every second.
    Then seconds = combinations / guesses_per_second, and we convert to human units.
    """
    if not pw:
        return "--"
    # A password in the attacker's wordlist is cracked instantly, no matter how
    # long it looks -- a "dictionary attack" tries known passwords first.
    common = ("password", "123456", "qwerty", "admin", "letmein", "null")
    if pw.lower() in common:
        return "instantly"
    pool = pool_size(pw)
    if pool == 0:
        return "instantly"
    combinations = pool ** len(pw)              # exponential growth!
    guesses_per_second = 10_000_000_000         # 10 billion (underscores aid reading)
    seconds = combinations / guesses_per_second

    # Walk up through time units until the number is small enough to say nicely.
    if seconds < 1:
        return "instantly"
    minute, hour, day, year = 60, 3600, 86400, 31536000
    if seconds < minute:
        return f"{seconds:.0f} seconds"
    if seconds < hour:
        return f"{seconds/minute:.0f} minutes"
    if seconds < day:
        return f"{seconds/hour:.0f} hours"
    if seconds < year:
        return f"{seconds/day:.0f} days"
    years = seconds / year
    if years < 1000:
        return f"{years:.0f} years"
    if years < 1_000_000:
        return f"{years/1000:.0f} thousand years"
    return "millions of years"


class Level1(Scene):
    """The actual playable screen. It INHERITS everything from Scene and adds
    its own state, plus its own handle_event / update / draw."""

    def __init__(self, game):
        super().__init__(game)            # let Scene set up self.game etc.
        # One text box for the player to type a password into.
        self.box = TextInput(60, 250, 520, 56, placeholder="type a strong password...")
        self.won = False
        # A "Continue" button that only appears after you win.
        self.continue_btn = Button(WIDTH - 240, HEIGHT - 90, 200, 56, "Continue >")
        # For a little flavor animation: a fake stream of guesses.
        self.fake_guess = "aaaaaa"
        self.anim_timer = 0.0

    def handle_event(self, event):
        self.box.handle_event(event)      # let the box collect typed keys
        if self.won and self.continue_btn.handle_event(event):
            self.next_scene = self.return_to  # leave to the debrief screen

    def update(self, dt):
        # Animate a scrolling "attacker is guessing" string for atmosphere.
        self.anim_timer += dt
        if self.anim_timer > 0.05:
            self.anim_timer = 0
            # Make a new random-looking 6-char string by rotating letters.
            self.fake_guess = "".join(
                chr(97 + (ord(c) - 97 + 1) % 26) for c in self.fake_guess
            )
        # Check the win condition every frame: score of 6+ counts as STRONG.
        score, _ = rate_password(self.box.text)
        if score >= 6:
            self.won = True

    def draw(self, surface):
        surface.fill(COLORS["bg"])
        self.draw_header(surface, "LEVEL 1  //  THE CRACKER")

        # Left side: the typing area and live feedback.
        draw_text(surface, "Build a password strong enough to lock NULL out.",
                  60, 100, size=22, color="white", max_width=560)
        draw_text(surface, "Attacker is guessing:  " + self.fake_guess + "...",
                  60, 150, size=18, color="red")
        self.box.draw(surface)

        score, tips = rate_password(self.box.text)

        # A strength meter: 6 little segments that light up with the score.
        meter_x, meter_y = 60, 330
        for i in range(6):
            lit = i < score
            color = COLORS["green"] if lit else COLORS["panel2"]
            pygame.draw.rect(surface, color, (meter_x + i * 88, meter_y, 80, 22),
                             border_radius=4)
        label = "STRONG" if score >= 6 else ("OK" if score >= 4 else "WEAK")
        label_color = "green" if score >= 6 else ("amber" if score >= 4 else "red")
        draw_text(surface, f"Strength: {label}  ({score}/6)",
                  60, 365, size=22, color=label_color)

        # The headline lesson: estimated time to brute-force.
        draw_text(surface, "Time for NULL to brute-force this:",
                  60, 415, size=20, color="gray")
        draw_text(surface, crack_time_text(self.box.text),
                  60, 442, size=30, color="cyan")

        # Tips on the right, in a panel.
        panel = pygame.Rect(640, 100, 320, 380)
        pygame.draw.rect(surface, COLORS["panel"], panel, border_radius=10)
        pygame.draw.rect(surface, COLORS["gray"], panel, width=1, border_radius=10)
        draw_text(surface, "ANALYSIS", 660, 116, size=20, color="amber")
        y = 150
        if not tips:
            draw_text(surface, "No weaknesses found. Excellent.", 660, y,
                      size=18, color="green", max_width=290)
        for t in tips:
            y = draw_text(surface, "- " + t, 660, y, size=17,
                          color="white", max_width=290) + 4

        # Win banner + continue button.
        if self.won:
            draw_text(surface, "VAULT SECURED. The Cracker is locked out!",
                      60, 510, size=24, color="green")
            self.continue_btn.draw(surface)
