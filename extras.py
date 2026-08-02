"""
extras.py  --  two bonus screens reachable from the main menu.
==============================================================

SandboxScene  -- "Free Play": just you and the Python terminal, with some handy
                 sample data already loaded so you can experiment with no goal.

GlossaryScene -- a scrollable, plain-English dictionary of every Python and
                 cybersecurity word the game uses. Scroll with the mouse wheel
                 or the Up/Down arrow keys.
"""

import pygame
from engine import Scene, Button, draw_text, COLORS, WIDTH, HEIGHT
from pyterminal import PyTerminal
from effects import MatrixRain


# ---------------------------------------------------------------------------
# FREE PLAY SANDBOX
# ---------------------------------------------------------------------------
class SandboxScene(Scene):
    def __init__(self, game):
        super().__init__(game)
        # Pre-load the terminal with sample data from across the game so there's
        # always something to poke at.
        seed = {
            "wordlist": ["123456", "password", "qwerty", "letmein", "dragon"],
            "services": {22: "SSH", 53: "DNS", 443: "HTTPS", 3306: "MySQL"},
            "email": {"sender": "support@amaz0n-verify.net",
                      "subject": "URGENT: verify now",
                      "body": "click here to verify your account"},
        }
        intro = [
            "# FREE PLAY -- experiment with no goal. Nothing here can break.",
            "# Pre-loaded for you:",
            "#   wordlist  -> a list of 5 common passwords",
            "#   services  -> a dict of port -> service name",
            "#   email     -> a dict with sender / subject / body",
            "# Try:  len(wordlist)   |   services[443]   |   email['sender']",
        ]
        self.term = PyTerminal(pygame.Rect(30, 90, 640, HEIGHT - 170),
                               seed=seed, intro=intro)
        self.back_btn = Button(30, HEIGHT - 64, 200, 48, "< Back to Menu",
                               color="gray")
        # "Clear" wipes the screen and restores the starting sample data.
        self.clear_btn = Button(250, HEIGHT - 64, 170, 48, "Clear Screen",
                                color="amber")
        # We type Python here, so don't let the global 'm'=mute shortcut steal the
        # letter m. Mute is available via the top-right button instead.
        self.captures_text = True
        # Faint falling-code background.
        self.rain = MatrixRain(WIDTH, HEIGHT)
        self.dim = pygame.Surface((WIDTH, HEIGHT))
        self.dim.fill(COLORS["bg"])
        self.dim.set_alpha(220)

    def handle_event(self, event):
        self.term.handle_event(event)
        if self.back_btn.handle_event(event):
            self.next_scene = "menu"
        if self.clear_btn.handle_event(event):
            self.term.reset()

    def update(self, dt):
        self.rain.update(dt)
        self.term.update(dt)

    def draw(self, surface):
        surface.fill(COLORS["bg"])
        self.rain.draw(surface)
        surface.blit(self.dim, (0, 0))
        self.draw_header(surface, "FREE PLAY  //  PYTHON SANDBOX")
        self.term.draw(surface)

        # A little cheat-sheet panel on the right.
        panel = pygame.Rect(690, 90, WIDTH - 720, HEIGHT - 170)
        pygame.draw.rect(surface, COLORS["panel"], panel, border_radius=10)
        pygame.draw.rect(surface, COLORS["gray"], panel, width=1, border_radius=10)
        y = draw_text(surface, "TRY THESE", 706, 104, size=20, color="amber")
        examples = [
            "2 + 2",
            "name = 'you'",
            "print('hi', name)",
            "len(wordlist)",
            "wordlist[0]",
            "services[22]",
            "email['subject']",
            "for w in wordlist:",
            "    print(w)",
            "",
            "(blank line runs",
            " a loop block)",
        ]
        y += 8
        for ex in examples:
            draw_text(surface, ex if ex else " ", 706, y, size=16, color="cyan")
            y += 24
        self.back_btn.draw(surface)
        self.clear_btn.draw(surface)


# ---------------------------------------------------------------------------
# GLOSSARY
# ---------------------------------------------------------------------------
# The content: a list of ("CATEGORY", [(term, definition), ...]) pairs.
GLOSSARY = [
    ("PYTHON BASICS", [
        ("variable", "A labeled box that stores a value, e.g.  age = 12. The name "
                     "'age' now points to the number 12."),
        ("string", "Text, written inside quotes:  \"hello\"  or  'hello'."),
        ("integer", "A whole number, like 7 or 65 (no decimal point)."),
        ("boolean", "A value that is either True or False -- used for yes/no answers."),
        ("list", "An ordered collection in square brackets:  [22, 53, 443]. "
                 "Read items by position:  ports[0] is the first."),
        ("dictionary", "A set of labeled values in curly braces:  "
                       "{'name': 'alice'}. Read by key:  user['name']."),
        ("function", "A named, reusable block of code. You 'call' it with ():  "
                     "len('hi') returns 2. Make your own with  def."),
        ("loop (for)", "Repeats code once for each item:  for w in wordlist: ... "
                       "Loops are how attackers try millions of guesses."),
        ("if / else", "Makes a decision: run some code only when a condition is "
                      "True, otherwise do something else."),
        ("class", "A blueprint for an 'object' that bundles data + behavior. "
                  "File('a.txt') makes a File object you read with a dot:  f.name."),
        ("f-string", "A string with variables dropped inside { }:  f\"hi {name}\". "
                     "Handy -- but gluing user input in is how SQL injection happens."),
        ("ord / chr", "ord('A') gives a letter's number (65); chr(65) gives the "
                      "letter back. Ciphers use this to do math on letters."),
        ("modulo (%)", "The remainder of a division:  26 % 26 is 0. Used to 'wrap "
                       "around' the alphabet from Z back to A."),
        ("print()", "Shows a value on the screen. Your main way to SEE what your "
                    "code is doing:  print('hello')."),
        ("comment (#)", "Anything after a # is a note for humans; Python ignores "
                        "it. Used to explain what code does."),
        ("index", "An item's position number, starting at 0. mylist[0] is the "
                  "first item; mylist[-1] is the last."),
        ("method", "A function that belongs to a value, called with a dot:  "
                   "'Hi'.lower(). Strings, lists and objects all have methods."),
        ("append()", "A list method that adds one item to the end:  "
                     "results.append(port)."),
        ("indentation", "The spaces at the start of a line. Python uses them to "
                        "know which lines belong inside a loop, if, or function."),
        ("error / exception", "Python's way of saying something went wrong (e.g. "
                              "NameError). The red text names the problem -- read "
                              "it, don't fear it."),
        ("None", "A special value meaning 'nothing here yet'. Functions that don't "
                 "return anything give back None."),
    ]),
    ("CYBERSECURITY", [
        ("brute-force", "Trying every possible password until one works. Fast "
                        "computers make short passwords fall in seconds."),
        ("dictionary attack", "Brute-force that starts with a list of common "
                              "passwords first, since so many people reuse them."),
        ("cipher", "A method to scramble a message so only someone with the key "
                   "can read it. The Caesar cipher just shifts each letter."),
        ("phishing", "A fake message that tricks a person into clicking a bad link "
                     "or giving up a password. Attacks the human, not the code."),
        ("port", "A numbered 'door' on a computer where a service listens. 443 is "
                 "secure web, 22 is remote login (SSH)."),
        ("backdoor", "A hidden way back into a system an attacker leaves behind, "
                     "often on an unusual port like 31337."),
        ("SQL injection", "Typing special text into a website so the database "
                          "treats it as a command. ' OR '1'='1  is the classic."),
        ("parameterized query", "The safe way to talk to a database: it keeps your "
                                "data and the command separate, blocking injection."),
        ("malware", "Any software built to harm or spy -- viruses, ransomware, "
                    "spyware. Often disguised as a harmless file."),
        ("double extension", "A filename like invoice.pdf.exe. It looks like a PDF "
                             "but the real ending (.exe) means it's a program."),
        ("ethical hacker", "Someone who uses attackers' techniques to FIND and FIX "
                           "weaknesses with permission. That's you."),
        ("hash", "A one-way scramble of data into a fixed code. Real systems store "
                 "the hash of your password, never the password itself."),
        ("encryption", "Scrambling data with a key so only someone with the key "
                       "can read it. Unlike a hash, it can be reversed."),
        ("firewall", "A guard that decides which network traffic is allowed in or "
                     "out -- it closes the doors attackers want open."),
        ("two-factor (2FA)", "A second proof of identity beyond your password, like "
                             "a code on your phone. Stops most stolen-password attacks."),
        ("vulnerability", "A weakness in software an attacker can abuse. Security "
                          "work is finding and fixing these first."),
        ("patch / update", "A fix released for a vulnerability. Installing updates "
                           "promptly closes the holes attackers rely on."),
        ("ransomware", "Malware that locks your files and demands payment. A big "
                       "reason to keep backups."),
        ("wordlist", "A large file of likely passwords that attackers try first in "
                     "a dictionary attack."),
        ("packet", "A small chunk of data sent over a network. Attackers 'sniff' "
                   "packets to read traffic they shouldn't see."),
    ]),
    ("STAYING SAFE (real-life tips)", [
        ("use long passphrases", "Four random words beat a short 'P@ss1'. Length "
                                 "is what defeats brute-force."),
        ("never reuse passwords", "If one site leaks, attackers try that password "
                                  "everywhere. A password manager remembers unique "
                                  "ones for you."),
        ("turn on 2FA", "Add a second factor on email and banking. Even a stolen "
                        "password won't be enough on its own."),
        ("think before you click", "Check the sender and hover over links. Urgency "
                                   "and fear are phishing's favorite tools."),
        ("keep software updated", "Updates patch the holes attackers exploit. "
                                  "'Remind me later' is how breaches happen."),
    ]),
]


class GlossaryScene(Scene):
    def __init__(self, game):
        super().__init__(game)
        self.scroll = 0                 # how far down we've scrolled, in pixels
        self.max_scroll = 0             # filled in while drawing
        self.back_btn = Button(30, HEIGHT - 64, 200, 48, "< Back to Menu",
                               color="gray")

    def handle_event(self, event):
        if self.back_btn.handle_event(event):
            self.next_scene = "menu"
        elif event.type == pygame.MOUSEWHEEL:
            self.scroll -= event.y * 40             # wheel up = scroll up
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_DOWN:
                self.scroll += 40
            elif event.key == pygame.K_UP:
                self.scroll -= 40
        # Keep scrolling within sensible limits.
        self.scroll = max(0, min(self.scroll, self.max_scroll))

    def draw(self, surface):
        surface.fill(COLORS["bg"])
        self.draw_header(surface, "GLOSSARY  //  WORDS YOU'VE LEARNED")

        # Only paint inside this region so text never spills onto the header/footer.
        top, bottom = 80, HEIGHT - 80
        surface.set_clip(pygame.Rect(0, top, WIDTH, bottom - top))

        y = top - self.scroll                       # subtract scroll to move content up
        for category, entries in GLOSSARY:
            y = draw_text(surface, category, 30, y, size=24, color="amber") + 4
            for term, definition in entries:
                draw_text(surface, term, 40, y, size=20, color="green")
                y = draw_text(surface, definition, 250, y, size=17, color="white",
                              max_width=WIDTH - 290, line_gap=3)
                y += 10
            y += 14

        surface.set_clip(None)                      # stop clipping

        # Work out how far the player is allowed to scroll: total height past the view.
        content_height = (y + self.scroll) - (top)
        self.max_scroll = max(0, content_height - (bottom - top))

        draw_text(surface, "Scroll with the mouse wheel or Up / Down arrows.",
                  260, HEIGHT - 52, size=15, color="gray")
        self.back_btn.draw(surface)


# ---------------------------------------------------------------------------
# LEVEL SELECT  (replay any level you've reached)
# ---------------------------------------------------------------------------
class LevelSelectScene(Scene):
    """Lets the player jump back into any unlocked level to retry it.

    A level is UNLOCKED if it's one you've already cleared, or it's the very next
    one to play. Levels further ahead stay LOCKED until you reach them. We read
    your saved progress from game.progress["completed"].
    """

    def __init__(self, game):
        super().__init__(game)
        self.rows = []                 # filled in draw(): (rect, level_no, unlocked)
        self.back_btn = Button(30, HEIGHT - 64, 200, 48, "< Back to Menu",
                               color="gray")
        self.rain = MatrixRain(WIDTH, HEIGHT)
        self.dim = pygame.Surface((WIDTH, HEIGHT))
        self.dim.fill(COLORS["bg"])
        self.dim.set_alpha(220)

    def unlocked(self, n):
        # Cleared levels and the next-up level are playable.
        return n <= self.game.progress["completed"] + 1

    def handle_event(self, event):
        if self.back_btn.handle_event(event):
            self.next_scene = "menu"
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for rect, n, unlocked in self.rows:
                if unlocked and rect.collidepoint(event.pos):
                    # Start that level from its briefing -- the full mission again.
                    self.next_scene = f"brief{n}"

    def update(self, dt):
        self.rain.update(dt)

    def draw(self, surface):
        surface.fill(COLORS["bg"])
        self.rain.draw(surface)
        surface.blit(self.dim, (0, 0))
        self.draw_header(surface, "SELECT LEVEL  //  REPLAY ANY MISSION")

        completed = self.game.progress["completed"]
        total = self.game.num_levels
        draw_text(surface, f"Cleared {completed} of {total}.  "
                  "Pick a mission to (re)play.", 30, 84, size=18, color="gray")

        # Lay the levels out in a grid so even ~30 of them fit on one screen.
        # One column up to 8 levels, otherwise two columns side by side.
        cols = 1 if total <= 8 else 2
        rows_per_col = -(-total // cols)        # ceiling division
        area_top, area_bottom = 110, HEIGHT - 80
        cell_h = min(54, (area_bottom - area_top) // rows_per_col)
        gap = 16
        cell_w = (WIDTH - 60 - (cols - 1) * gap) // cols

        self.rows = []
        for n in range(1, total + 1):
            idx = n - 1
            col = idx // rows_per_col           # fill column by column
            row_in_col = idx % rows_per_col
            x = 30 + col * (cell_w + gap)
            y = area_top + row_in_col * cell_h
            unlocked = self.unlocked(n)
            rect = pygame.Rect(x, y, cell_w, cell_h - 6)
            self.rows.append((rect, n, unlocked))

            if n <= completed:
                border, badge, bcolor = "green", "CLEARED", "green"
            elif unlocked:
                border, badge, bcolor = "cyan", "PLAY", "cyan"
            else:
                border, badge, bcolor = "gray", "LOCKED", "gray"

            hover = unlocked and rect.collidepoint(pygame.mouse.get_pos())
            bg = COLORS["panel2"] if hover else COLORS["panel"]
            pygame.draw.rect(surface, bg, rect, border_radius=6)
            pygame.draw.rect(surface, COLORS[border], rect, width=2, border_radius=6)

            name_color = "white" if unlocked else "gray"
            cy = rect.y + (rect.height - 18) // 2
            draw_text(surface, f"{n}.", rect.x + 12, cy, size=16, color=bcolor)
            draw_text(surface, self.game.level_names[n - 1],
                      rect.x + 52, cy, size=18, color=name_color)
            draw_text(surface, badge, rect.right - 110, cy + 1, size=15, color=bcolor)

        self.back_btn.draw(surface)
