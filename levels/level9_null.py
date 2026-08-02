"""
LEVEL 7  --  NULL   (The final boss -- everything you learned)
=============================================================

Security idea you learn:
    Real attackers don't use just one trick -- they chain them. NULL throws one
    challenge from each domain at you: passwords, cryptography, phishing,
    networks, web injection, and malware. Then you seal NULL away by doing what
    Level 1 taught: setting a password strong enough that it can never brute-force.

Python you learn:
    - reusing code from another file (we import rate_password from Level 1!)
    - a list of question dictionaries driving a quiz loop
    - tracking game state: NULL's "health", the current round, win/lose
    - bringing every earlier idea together in one scene

How the level plays:
    Answer each multiple-choice challenge correctly to damage NULL. Clear all eight,
    then type a strong final password to lock NULL away forever.
"""

import pygame
from engine import Scene, Button, TextInput, draw_text, COLORS, WIDTH, HEIGHT
# Reuse the password scorer we already wrote in Level 1 -- no copy-paste!
from levels.level1_passwords import rate_password


# ===========================================================================
# INTEL  --  what NULL does.
# ===========================================================================
INTEL = [
    {
        "heading": "What NULL does",
        "body": "NULL doesn't use one trick -- it CHAINS them. Phish an employee "
                "for a password, crack the weak ones, slip through an open port, "
                "inject the database, plant malware, and cover the tracks. Real "
                "attacks are a sequence, often scripted end to end:",
        "code": "steps = [phish, crack, scan_ports, inject, deploy_malware]\n"
                "for step in steps:\n"
                "    step(target)",
    },
    {
        "heading": "The defender thinks the same way",
        "body": "You'll defend the same way you'd attack: with small functions you "
                "can combine. A password auditor, an alert counter, a scanner -- "
                "each is a few lines, and together they're a security toolkit. The "
                "lab's final challenges combine everything you've practiced.",
        "code": None,
    },
    {
        "heading": "This is the last stand",
        "body": "Beat the two capstone challenges, then the eight-round boss gauntlet, "
                "then seal NULL with one final unbreakable password. Everything the "
                "lieutenants taught you comes down to this.",
        "code": None,
    },
]


# ===========================================================================
# CHALLENGES  --  the capstone. These combine skills from earlier levels.
# ===========================================================================
def _check_strength(t):
    f = t.ns.get("strength")
    if not callable(f):
        return False
    try:
        # "password": short, no digit, no upper -> 0.
        # "LongPassword12": 12+ chars, has digit, has upper -> 3.
        return f("password") == 0 and f("LongPassword12") == 3
    except Exception:
        return False

def _check_criticals(t):
    return t.ns.get("criticals") == 2

def _check_filter(t):
    return t.ns.get("strong") == ["verylongpassword", "anotherlongone1"]

CHALLENGES = [
    {
        "title": "Filter the strong passwords",
        "goal": "`passwords` is a list. Build a new list called `strong` containing "
                "only the ones with 12 or more characters. A loop with an `if` and "
                ".append() works perfectly here.",
        "seed": lambda: {"passwords": ["abc", "verylongpassword", "hi",
                                       "anotherlongone1"]},
        "intro": ["# `passwords` is preloaded. Keep only the long ones (len >= 12).",
                  "# Start:  strong = []   then loop, and strong.append(p) when long."],
        "hint": "strong = []  /  for p in passwords:  /  if len(p) >= 12:  /  strong.append(p)",
        "solution": "strong = []\nfor p in passwords:\n    if len(p) >= 12:\n"
                    "        strong.append(p)",
        "check": _check_filter,
        "success": "You filtered a list down to what matters -- a core everyday skill.",
    },
    {
        "title": "Capstone: password auditor",
        "goal": "Write a function `strength(pw)` that returns a score from 0 to 3: "
                "+1 if pw is 12+ characters, +1 if it contains any digit, +1 if it "
                "contains any uppercase letter. Use any(...) for the checks.",
        "intro": ["# def strength(pw):  return an int 0..3",
                  "# +1 length>=12,  +1 any digit,  +1 any uppercase.",
                  "# Tip:  any(c.isdigit() for c in pw)"],
        "hint": "score = 0; then  if len(pw) >= 12: score += 1; "
                "if any(c.isdigit() for c in pw): score += 1; "
                "if any(c.isupper() for c in pw): score += 1; return score",
        "solution": "def strength(pw):\n    score = 0\n    if len(pw) >= 12:\n"
                    "        score += 1\n    if any(c.isdigit() for c in pw):\n"
                    "        score += 1\n    if any(c.isupper() for c in pw):\n"
                    "        score += 1\n    return score",
        "check": _check_strength,
        "success": "A working auditor -- the Level 1 idea, now a reusable function.",
    },
    {
        "title": "Capstone: triage the alerts",
        "goal": "`alerts` is a list of dicts, each with a 'level' key. Count how "
                "many have level equal to 'critical' and store the total in "
                "`criticals`. (Lists + dicts + a counting loop -- all together.)",
        "seed": lambda: {"alerts": [
            {"id": 1, "level": "info"},
            {"id": 2, "level": "critical"},
            {"id": 3, "level": "warning"},
            {"id": 4, "level": "critical"}]},
        "intro": ["# `alerts` = list of dicts with a 'level' key.",
                  "# Count the 'critical' ones into `criticals`."],
        "hint": "criticals = 0  /  for a in alerts:  /  if a['level'] == 'critical':  /  criticals += 1",
        "solution": "criticals = 0\nfor a in alerts:\n    if a['level'] == 'critical':\n"
                    "        criticals += 1",
        "check": _check_criticals,
        "success": "Two criticals found. You've combined every core skill. Now end this.",
    },
]


# Each round is a dictionary: a prompt, four options, and the correct index.
ROUNDS = [
    {"skill": "PASSWORDS",
     "q": "NULL demands the strongest password. Which resists brute-force best?",
     "options": ["password1", "Tr0ub4dor", "correct-horse-battery-staple-92!", "abc123"],
     "answer": 2},
    {"skill": "CRYPTOGRAPHY",
     "q": "Decrypt this Caesar text (shift 1):  'IFMMP'",
     "options": ["HELLO", "WORLD", " HELP ", "GHOST"],
     "answer": 0},
    {"skill": "PHISHING",
     "q": "Which sender is most likely a phishing impersonation?",
     "options": ["billing@github.com", "support@amaz0n-verify.net",
                 "no-reply@slack.com", "team@your-company.com"],
     "answer": 1},
    {"skill": "NETWORKS",
     "q": "Four ports are open. Which screams 'backdoor'?",
     "options": ["443 HTTPS", "22 SSH", "53 DNS", "31337 remote shell -> unknown IP"],
     "answer": 3},
    {"skill": "WEB INJECTION",
     "q": "Which login input is a SQL injection attempt?",
     "options": ["alice", "' OR '1'='1", "admin123", "guest"],
     "answer": 1},
    {"skill": "MALWARE",
     "q": "Which file is almost certainly malware?",
     "options": ["report.pdf", "photo.jpg", "invoice.pdf.exe", "notes.txt"],
     "answer": 2},
    {"skill": "HASHING",
     "q": "Why do good websites store password HASHES instead of passwords?",
     "options": ["Hashes are shorter", "A hash can't be reversed back to the password",
                 "It looks more professional", "Hashes never need updating"],
     "answer": 1},
    {"skill": "2FA",
     "q": "'IT Security' texts you asking for your 6-digit code. You should:",
     "options": ["Reply quickly to be safe", "Refuse -- real services never ask",
                 "Send half of it", "Call them back and read it out"],
     "answer": 1},
]


class Level9(Scene):
    def __init__(self, game):
        super().__init__(game)
        self.round = 0                 # which question we're on (0-7)
        self.health = len(ROUNDS)      # NULL's health = number of rounds
        self.phase = "quiz"            # "quiz" -> "lockdown" -> "won"
        self.feedback = ""
        self.option_btns = []          # rebuilt each round
        self.build_buttons()
        # The final lockdown uses a password box, just like Level 1.
        self.box = TextInput(60, 330, WIDTH - 120, 56,
                             placeholder="type a final, brute-force-proof password...")
        self.continue_btn = Button(WIDTH - 240, HEIGHT - 90, 200, 56, "Finish >")

    def build_buttons(self):
        """Create one button per answer option for the current round."""
        self.option_btns = []
        if self.round >= len(ROUNDS):
            return
        opts = ROUNDS[self.round]["options"]
        for i, text in enumerate(opts):
            # Stack the four options vertically.
            self.option_btns.append(
                Button(60, 250 + i * 64, WIDTH - 120, 56, text, color="cyan")
            )

    def handle_event(self, event):
        if self.phase == "quiz":
            for i, btn in enumerate(self.option_btns):
                if btn.handle_event(event):
                    if i == ROUNDS[self.round]["answer"]:
                        self.health -= 1            # land a hit on NULL
                        self.feedback = "HIT! NULL staggers."
                        self.round += 1
                        if self.round >= len(ROUNDS):
                            self.phase = "lockdown"  # all eight skills proven
                        else:
                            self.build_buttons()
                    else:
                        self.feedback = "Blocked. NULL counters -- try again."

        elif self.phase == "lockdown":
            self.box.handle_event(event)
            score, _ = rate_password(self.box.text)
            if score >= 6:
                self.phase = "won"

        else:  # won
            if self.continue_btn.handle_event(event):
                self.next_scene = self.return_to

    def draw(self, surface):
        surface.fill(COLORS["bg"])
        self.draw_header(surface, "FINAL BOSS  //  NULL")

        # NULL's health bar across the top of the play area.
        draw_text(surface, "NULL INTEGRITY", 60, 90, size=18, color="purple")
        bar = pygame.Rect(60, 115, WIDTH - 120, 24)
        pygame.draw.rect(surface, COLORS["panel2"], bar, border_radius=6)
        if self.health > 0:
            frac = self.health / len(ROUNDS)
            fill = pygame.Rect(60, 115, int((WIDTH - 120) * frac), 24)
            pygame.draw.rect(surface, COLORS["purple"], fill, border_radius=6)

        if self.phase == "quiz":
            r = ROUNDS[self.round]
            draw_text(surface, f"ROUND {self.round + 1}/{len(ROUNDS)}  --  {r['skill']}",
                      60, 165, size=20, color="amber")
            draw_text(surface, r["q"], 60, 200, size=22, color="white",
                      max_width=WIDTH - 120)
            for btn in self.option_btns:
                btn.draw(surface)
            if self.feedback:
                draw_text(surface, self.feedback, 60, 250 + 4 * 64, size=20,
                          color="green" if "HIT" in self.feedback else "red")

        elif self.phase == "lockdown":
            draw_text(surface, "NULL is on the ropes. Seal it away for good:",
                      60, 200, size=24, color="white")
            draw_text(surface, "Type a password strong enough that NULL can never "
                      "brute-force its way back (length + variety, like Level 1).",
                      60, 245, size=18, color="gray", max_width=WIDTH - 120)
            self.box.draw(surface)
            score, _ = rate_password(self.box.text)
            draw_text(surface, f"Lock strength: {score}/6", 60, 410, size=22,
                      color="green" if score >= 6 else "amber")

        else:  # won
            draw_text(surface, "NULL SEALED. THE COLLECTIVE IS FINISHED.",
                      60, 230, size=30, color="green", max_width=WIDTH - 120)
            draw_text(surface, "You chained all eight skills and locked the leader "
                      "away. The city is safe.", 60, 285, size=22, color="white",
                      max_width=WIDTH - 120)
            self.continue_btn.draw(surface)
