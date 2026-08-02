"""
LEVEL 4  --  GHOST   (Networks, ports & intrusion detection)
============================================================

Security idea you learn:
    Computers talk over numbered "ports" -- think of them as doors, each used by
    a particular service. Web traffic uses port 80/443, secure logins use 22,
    email uses 25. Attackers open a secret "backdoor" on an unusual port so they
    can sneak back in. A defender scans the open ports and spots the odd one out.

Python you learn:
    - a list of dictionaries describing each open connection
    - random.shuffle to mix the order so the answer moves each play
    - looping with enumerate to get BOTH the position and the item
    - detecting a mouse click inside a rectangle

How the level plays:
    Ghost left a backdoor running on this server. Read the port scan, find the
    one connection that doesn't belong, and click it to kill the intruder.
"""

import random
import pygame
from engine import Scene, Button, draw_text, COLORS, WIDTH, HEIGHT


# ===========================================================================
# INTEL  --  what Ghost does.
# ===========================================================================
INTEL = [
    {
        "heading": "What Ghost does",
        "body": "Every computer has 65,535 numbered 'ports' -- doors where services "
                "listen. Ghost runs a 'port scan' to find which doors are open, "
                "then leaves a backdoor on an odd one. The scan itself is just a "
                "loop over port numbers:",
        "code": "for port in range(1, 65536):\n"
                "    if is_open(host, port):\n"
                "        print('open port found:', port)",
    },
    {
        "heading": "Known doors vs. strangers",
        "body": "Defenders keep a map of which ports SHOULD be open and what runs "
                "on them. A dictionary is perfect: the port number is the key, the "
                "service is the value. Anything open that isn't in the map is a "
                "red flag worth investigating.",
        "code": "services = {22: 'SSH', 53: 'DNS', 443: 'HTTPS'}\n"
                "print(services[443])      # -> 'HTTPS'\n"
                "if port not in services:  # an unexpected open door\n"
                "    alert('unknown service on', port)",
    },
    {
        "heading": "Real scenario",
        "body": "Backdoors love high, memorable ports -- 31337 spells 'eleet' in "
                "hacker slang. A defender scans, compares every open port against "
                "the known-good list, and pounces on the odd one out. That's "
                "exactly the boss fight; first you'll build the logic in the lab.",
        "code": None,
    },
]


# ===========================================================================
# CHALLENGES
# ===========================================================================
def _check_svc(t):
    return t.ns.get("svc") == "SSH"

def _check_backdoor(t):
    return t.ns.get("is_backdoor") is True

def _check_bad(t):
    return t.ns.get("bad") == [31337]

def _check_total(t):
    return t.ns.get("total") == 4

def _check_isopen(t):
    return t.ns.get("is_open") is True

CHALLENGES = [
    {
        "title": "Look it up",
        "goal": "`services` is a dictionary mapping port numbers to service names. "
                "Look up port 22 and store the result in `svc`. Dictionaries are "
                "accessed with square brackets:  services[22].",
        "seed": lambda: {"services": {22: "SSH", 53: "DNS", 443: "HTTPS",
                                      3306: "MySQL"}},
        "intro": ["# `services` maps port -> name. Try:  services[443]",
                  "# Store the service running on port 22 in `svc`."],
        "hint": "svc = services[22]",
        "solution": "svc = services[22]",
        "check": _check_svc,
        "success": "Port 22 is SSH. A dict turns a number straight into an answer.",
    },
    {
        "title": "Count the open doors",
        "goal": "len() also counts items in a list. Store how many ports are in "
                "`open_ports` in a variable named `total`.",
        "seed": lambda: {"open_ports": [22, 443, 31337, 53]},
        "intro": ["# `open_ports` is a list. Try:  len(open_ports)",
                  "# Store the count in `total`."],
        "hint": "total = len(open_ports)",
        "solution": "total = len(open_ports)",
        "check": _check_total,
        "success": "Four doors open. len() counts list items just like string characters.",
    },
    {
        "title": "Is this port open?",
        "goal": "Use `in` to check membership in a list. Set `is_open` to whether "
                "port 443 appears in `open_ports`.",
        "seed": lambda: {"open_ports": [22, 443, 31337, 53]},
        "intro": ["# Is 443 in the list?  Try:  443 in open_ports",
                  "# Store the True/False answer in `is_open`."],
        "hint": "is_open = 443 in open_ports",
        "solution": "is_open = 443 in open_ports",
        "check": _check_isopen,
        "success": "443 is open. `in` answers 'is this thing in that collection?'",
    },
    {
        "title": "Is this door known?",
        "goal": "`known` lists the ports that are supposed to be open. Set "
                "`is_backdoor` to True if `port` is NOT in `known`. Use the "
                "`not in` test.",
        "seed": lambda: {"port": 31337, "known": [22, 53, 443, 3306]},
        "intro": ["# `port` = 31337, `known` = the allowed ports.",
                  "# Is `port` missing from `known`?  Try:  port not in known"],
        "hint": "is_backdoor = port not in known",
        "solution": "is_backdoor = port not in known",
        "check": _check_backdoor,
        "success": "31337 isn't on the allow-list -- flagged as a backdoor.",
    },
    {
        "title": "Find every intruder",
        "goal": "`open_ports` lists all open ports. `known` lists the safe ones. "
                "Loop over open_ports and collect every port that's NOT known into "
                "a list called `bad`.",
        "seed": lambda: {"open_ports": [22, 443, 31337, 53],
                         "known": [22, 53, 443, 3306]},
        "intro": ["# Build a list `bad` of the suspicious open ports.",
                  "# Start:  bad = []   then loop and bad.append(port) when unknown."],
        "hint": "bad = []  /  for port in open_ports:  /  if port not in known:  /  bad.append(port)",
        "solution": "bad = []\nfor port in open_ports:\n    if port not in known:\n"
                    "        bad.append(port)",
        "check": _check_bad,
        "success": "You isolated Ghost's backdoor port (31337) with pure Python.",
    },
]


# Each row is a dictionary. `evil` marks Ghost's hidden backdoor.
# The legit rows use well-known ports with matching, expected services.
PORTS = [
    {"port": 443,   "service": "HTTPS (secure web)",       "evil": False,
     "note": "Standard encrypted web traffic. Expected."},
    {"port": 22,    "service": "SSH (remote admin)",       "evil": False,
     "note": "Used by admins to log in securely. Expected on a server."},
    {"port": 53,    "service": "DNS (name lookup)",        "evil": False,
     "note": "Translates names to addresses. Normal background service."},
    {"port": 3306,  "service": "MySQL (database)",         "evil": False,
     "note": "The site's database. Expected for this app."},
    {"port": 31337, "service": "remote shell -> 9.9.9.9",  "evil": True,
     "note": "An obscure high port quietly piping a COMMAND SHELL to an unknown "
             "outside address. That's Ghost's backdoor."},
    {"port": 25,    "service": "SMTP (outgoing email)",    "evil": False,
     "note": "Sends mail. Normal for a server that emails users."},
]


class Level4(Scene):
    def __init__(self, game):
        super().__init__(game)
        # Copy the list so we can shuffle without disturbing the original.
        self.rows = PORTS[:]                     # [:] makes a shallow copy
        random.shuffle(self.rows)                # the backdoor's spot changes each play
        self.selected = None                     # which row index the player clicked
        self.won = False
        self.row_rects = []                      # filled in during draw(), used by clicks
        self.continue_btn = Button(WIDTH - 240, HEIGHT - 90, 200, 56, "Continue >")
        self.message = "Click the connection that does NOT belong."

    def handle_event(self, event):
        if self.won:
            if self.continue_btn.handle_event(event):
                self.next_scene = self.return_to
            return
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # Check each row rectangle to see which (if any) was clicked.
            for i, rect in enumerate(self.row_rects):
                if rect.collidepoint(event.pos):
                    self.selected = i
                    if self.rows[i]["evil"]:
                        self.won = True
                        self.message = "BACKDOOR KILLED. Ghost is cut off!"
                    else:
                        self.message = "That one's legitimate -- keep scanning."

    def draw(self, surface):
        surface.fill(COLORS["bg"])
        self.draw_header(surface, "LEVEL 4  //  GHOST")

        draw_text(surface, "PORT SCAN -- open connections on the compromised server:",
                  60, 90, size=20, color="gray")
        draw_text(surface, self.message, 60, 120, size=20,
                  color="green" if self.won else "amber")

        # Draw each connection as a clickable row, and remember its rectangle.
        self.row_rects = []
        y = 165
        for i, row in enumerate(self.rows):
            rect = pygame.Rect(60, y, WIDTH - 120, 60)
            self.row_rects.append(rect)
            # Highlight the row the player last clicked.
            if self.won and row["evil"]:
                bg = COLORS["red"]
            elif self.selected == i:
                bg = COLORS["panel2"]
            else:
                bg = COLORS["panel"]
            pygame.draw.rect(surface, bg, rect, border_radius=8)
            pygame.draw.rect(surface, COLORS["gray"], rect, width=1, border_radius=8)
            draw_text(surface, f"PORT {row['port']:<6}", 80, y + 18, size=22, color="cyan")
            draw_text(surface, row["service"], 250, y + 18, size=22, color="white")
            # Reveal the explanation once a row has been inspected.
            if self.selected == i or (self.won and row["evil"]):
                draw_text(surface, row["note"], 80, y + 44, size=15, color="gray",
                          max_width=WIDTH - 200)
                rect.height = 80          # let the next row sit lower (visual only)
            y += rect.height + 8

        if self.won:
            self.continue_btn.draw(surface)
