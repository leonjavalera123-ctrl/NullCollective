"""
LEVEL 5  --  THE INJECTOR   (Web security: SQL injection)
=========================================================

Security idea you learn:
    Websites store data in a database and ask for it with "queries" written in a
    language called SQL. A careless site builds the query by gluing your typed
    text straight into it. If you type cleverly, your text can CHANGE the query's
    meaning -- that's a "SQL injection". The classic payload  ' OR '1'='1
    turns a login check into something that is always true, letting you walk in.

Python you learn:
    - f-strings: building a string with your variables dropped inside { }
    - checking what a string CONTAINS with the `in` keyword
    - .lower() to compare text without worrying about capitalization
    - why "never trust user input" is a rule, with a live demo

How the level plays:
    Phase 1: break into NULL's stolen-data server by injecting the login form.
    Phase 2: now play defender -- choose the fix that stops the very attack you used.
"""

import pygame
from engine import Scene, Button, TextInput, draw_text, COLORS, WIDTH, HEIGHT


# ===========================================================================
# INTEL  --  what The Injector does.
# ===========================================================================
INTEL = [
    {
        "heading": "What The Injector does",
        "body": "Websites ask a database for data using 'queries' written in SQL. "
                "A careless site builds the query by gluing your typed text right "
                "into it with an f-string. The Injector types text that the "
                "database mistakes for a COMMAND instead of data:",
        "code": "# the vulnerable site does this:\n"
                "query = f\"SELECT * FROM users WHERE name = '{user_input}'\"\n"
                "# if user_input is:   ' OR '1'='1\n"
                "# the query becomes always-true -> attacker logs in as anyone",
    },
    {
        "heading": "Why the payload works",
        "body": "The input  ' OR '1'='1  closes the original quote, then adds a "
                "condition ('1'='1') that is ALWAYS true. The login check passes "
                "for every row. The fix is to never mix data into commands -- real "
                "code uses 'parameterized queries' that keep them separate.",
        "code": "# SAFE: the value can never become a command\n"
                "cursor.execute('SELECT * FROM users WHERE name = ?', (user_input,))",
    },
    {
        "heading": "Real scenario",
        "body": "SQL injection has leaked hundreds of millions of records over the "
                "years and still ranks among the top web risks. In the lab you'll "
                "build the vulnerable query, craft the payload, and write a detector "
                "-- so you can recognize and stop it.",
        "code": None,
    },
]


# ===========================================================================
# CHALLENGES
# ===========================================================================
def _check_query(t):
    q = t.ns.get("query", "")
    return isinstance(q, str) and "alice" in q and q.upper().startswith("SELECT")

def _check_attack_fn(t):
    f = t.ns.get("is_attack")
    if not callable(f):
        return False
    try:
        return f("' OR '1'='1") is True and f("alice") is False
    except Exception:
        return False

def _check_clean(t):
    f = t.ns.get("clean")
    if not callable(f):
        return False
    try:
        return "'" not in f("a' OR '1'='1")
    except Exception:
        return False

def _check_hasquote(t):
    return t.ns.get("has_quote") is True

def _check_quotes(t):
    return t.ns.get("quotes") == 2

CHALLENGES = [
    {
        "title": "Build a query with an f-string",
        "goal": "An f-string drops a variable's value inside a string using { }. "
                "Build a login query from `user` and store it in `query`. It should "
                "look like:  SELECT * FROM users WHERE name = '<user>'",
        "seed": lambda: {"user": "alice"},
        "intro": ["# `user` = 'alice'. An f-string:  f\"hi {user}\"",
                  "# Build the SELECT query into a variable named `query`."],
        "hint": "query = f\"SELECT * FROM users WHERE name = '{user}'\"",
        "solution": "query = f\"SELECT * FROM users WHERE name = '{user}'\"",
        "check": _check_query,
        "success": "That's how the vulnerable site builds its query -- by gluing input in.",
    },
    {
        "title": "Find the dangerous character",
        "goal": "A single quote ( ' ) is what lets an attacker break out of a "
                "string. Set `has_quote` to True if `user` contains a single quote, "
                "using the `in` test.",
        "seed": lambda: {"user": "alice'--"},
        "intro": ["# `user` is some typed input. Does it contain a ' character?",
                  "# Try:  \"'\" in user   -> True or False"],
        "hint": "has_quote = \"'\" in user",
        "solution": "has_quote = \"'\" in user",
        "check": _check_hasquote,
        "success": "A quote in the input is a warning sign worth checking for.",
    },
    {
        "title": "Count the quotes",
        "goal": "The .count() method counts how many times something appears. Store "
                "the number of single quotes in `user` in a variable named `quotes`.",
        "seed": lambda: {"user": "a' OR 'x"},
        "intro": ["# Try:  user.count(\"'\")",
                  "# Store the result in `quotes`."],
        "hint": "quotes = user.count(\"'\")",
        "solution": "quotes = user.count(\"'\")",
        "check": _check_quotes,
        "success": "Two quotes -- a telltale shape of an injection attempt.",
    },
    {
        "title": "Write the detector",
        "goal": "Write a function `is_attack(text)` that returns True if `text` "
                "contains a SQL-injection attempt. Detect the always-true trick: "
                "return True when \"or '1'='1\" is in text.lower().",
        "intro": ["# Define:  def is_attack(text):",
                  "# Return True if the classic ' OR '1'='1 pattern is present.",
                  "# Test:  is_attack(\"' OR '1'='1\")  should be True."],
        "hint": "def is_attack(text):  /  return \"or '1'='1\" in text.lower()",
        "solution": "def is_attack(text):\n    return \"or '1'='1\" in text.lower()",
        "check": _check_attack_fn,
        "success": "Your detector flags the payload but lets 'alice' through. That's a defense.",
    },
    {
        "title": "Sanitize the input",
        "goal": "One crude defense is to strip dangerous characters. Write a "
                "function `clean(text)` that returns `text` with every single-quote "
                "(') removed, so it can't break out of the string.",
        "intro": ["# Define:  def clean(text):  and return text with ' removed.",
                  "# Tip: the .replace(old, new) string method.",
                  "# (Real apps use parameterized queries -- this shows the idea.)"],
        "hint": "def clean(text):  /  return text.replace(\"'\", \"\")",
        "solution": "def clean(text):\n    return text.replace(\"'\", \"\")",
        "check": _check_clean,
        "success": "No quotes survive -> the injection can't escape the string anymore.",
    },
]


def build_query(username):
    """Show how the vulnerable server builds its login query from your input.

    The site does the equivalent of this f-string. Notice your text lands
    INSIDE the quotes -- so if your text contains a quote, you escape the box.
    """
    return f"SELECT * FROM accounts WHERE user = '{username}' AND active = 1;"


def is_injection(username):
    """Return True if the typed text is a working 'always true' SQL injection.

    A real database would parse this, but we can recognize the classic shape:
    a quote to break out, then an OR with a condition that's always true.
    """
    t = username.lower()
    # It must break out of the quoted string AND add an always-true OR clause.
    broke_out = "'" in t
    always_true = ("or '1'='1" in t) or ("or 1=1" in t) or ("or '1' = '1'" in t)
    return broke_out and always_true


class Level5(Scene):
    def __init__(self, game):
        super().__init__(game)
        self.phase = 1                 # 1 = attack, 2 = defend
        self.box = TextInput(60, 250, WIDTH - 120, 56,
                             placeholder="enter username...", max_len=60)
        self.login_btn = Button(60, 330, 200, 56, "Login", color="cyan")
        self.feedback = "Hint: try   ' OR '1'='1"
        self.broke_in = False
        # Phase 2 defense options. Exactly one is the correct fix.
        self.fix_btns = [
            Button(60, 250, WIDTH - 120, 56,
                   "A) Tell users not to type quote marks", color="gray"),
            Button(60, 320, WIDTH - 120, 56,
                   "B) Use parameterized queries (keep data and commands separate)",
                   color="green"),
            Button(60, 390, WIDTH - 120, 56,
                   "C) Hide the error messages so attacks fail silently", color="gray"),
        ]
        self.correct_fix = 1           # index B is the right answer
        self.fix_feedback = ""
        self.won = False
        self.continue_btn = Button(WIDTH - 240, HEIGHT - 90, 200, 56, "Continue >")

    def handle_event(self, event):
        if self.phase == 1:
            self.box.handle_event(event)
            if self.login_btn.handle_event(event):
                if not self.broke_in:
                    # First job: actually break in with an injection.
                    if is_injection(self.box.text):
                        self.broke_in = True
                        self.feedback = "ACCESS GRANTED. The query was always true -- you're in!"
                    elif self.box.text:
                        self.feedback = f"'{self.box.text}' is not a valid account. Try the injection."
                else:
                    # Already inside: this same button (now 'Continue') advances.
                    self.phase = 2

        elif self.phase == 2 and not self.won:
            for i, btn in enumerate(self.fix_btns):
                if btn.handle_event(event):
                    if i == self.correct_fix:
                        self.won = True
                        self.fix_feedback = "Correct. Parameterized queries treat your input as DATA, never as a command."
                    else:
                        self.fix_feedback = "That doesn't actually stop the attack. Try again."
        else:
            if self.continue_btn.handle_event(event):
                self.next_scene = self.return_to

    def draw(self, surface):
        surface.fill(COLORS["bg"])
        self.draw_header(surface, "LEVEL 5  //  THE INJECTOR")

        if self.phase == 1:
            draw_text(surface, "NULL's stolen-data server login. Break in.",
                      60, 90, size=22, color="white")
            draw_text(surface, "The server builds this query from your input:",
                      60, 140, size=18, color="gray")
            # Live preview of the query with the player's text injected.
            qpanel = pygame.Rect(60, 170, WIDTH - 120, 60)
            pygame.draw.rect(surface, COLORS["panel"], qpanel, border_radius=8)
            draw_text(surface, build_query(self.box.text or "..."), 76, 188,
                      size=18, color="cyan", max_width=WIDTH - 150)
            self.box.draw(surface)

            if not self.broke_in:
                self.login_btn.label = "Login"
                self.login_btn.draw(surface)
            else:
                # Repurpose the button to move on, once we're inside.
                self.login_btn.label = "Continue >"
                self.login_btn.draw(surface)

            color = "green" if self.broke_in else "amber"
            draw_text(surface, self.feedback, 60, 410, size=20, color=color,
                      max_width=WIDTH - 120)

        else:  # phase 2 -- defender
            draw_text(surface, "Now defend it. You broke in because the site trusted "
                      "your input. Which fix actually stops this?",
                      60, 100, size=22, color="white", max_width=WIDTH - 120)
            for btn in self.fix_btns:
                btn.draw(surface)
            if self.fix_feedback:
                draw_text(surface, self.fix_feedback, 60, 460, size=20,
                          color="green" if self.won else "red", max_width=WIDTH - 120)
            if self.won:
                # Run the player's OWN clean() from the lab, if they wrote one, to
                # show it neutralizing the exact payload they used to break in.
                clean = self.game.toolkit.get("clean")
                if callable(clean):
                    try:
                        payload = "' OR '1'='1"
                        result = clean(payload)
                        draw_text(surface, "Powered by your Lab code:  "
                                  f"clean(\"{payload}\")  ->  \"{result}\"",
                                  60, 500, size=18, color="cyan",
                                  max_width=WIDTH - 120)
                        draw_text(surface, "The quotes you stripped mean the attack "
                                  "can no longer escape the string.", 60, 528,
                                  size=16, color="gray", max_width=WIDTH - 120)
                    except Exception:
                        pass
                self.continue_btn.draw(surface)
