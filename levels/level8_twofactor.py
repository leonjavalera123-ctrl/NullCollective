"""
LEVEL 8  --  RELAY   (Two-factor authentication & one-time codes)
=================================================================

Security idea you learn:
    A password is "something you know". Two-factor authentication (2FA) adds
    "something you have" -- usually a 6-digit code on your phone that changes
    constantly. Even if NULL steals your password, it can't log in without that
    code. The codes come from simple math on a shared secret. RELAY's only hope
    is to TRICK you into reading your code aloud -- so the rule is: never share it.

Python you learn:
    - the modulo % operator to keep a number to 6 digits
    - .zfill(6) to pad a short number with leading zeros
    - writing a code generator function
    - comparing values to verify a code

How the level plays:
    First RELAY phishes you for your code -- refuse it. Then NULL tries to log in
    with your stolen password; read your authenticator and enter the code to deny it.
"""

import pygame
from engine import Scene, Button, TextInput, draw_text, COLORS, WIDTH, HEIGHT


# ===========================================================================
# INTEL
# ===========================================================================
INTEL = [
    {"heading": "What RELAY does",
     "body": "RELAY can't beat 2FA with code, so it attacks the human: fake "
             "'security check' messages that beg you to read out the 6-digit code "
             "just texted to you. Hand it over and RELAY types it in before it "
             "expires. The defense is a habit: a real company NEVER asks for your code.",
     "code": "# RELAY's lie:\n"
             "'This is IT Security. Reply with the code we just sent to verify you.'"},
    {"heading": "How the codes are made",
     "body": "Your phone and the server share a secret number. They combine it with "
             "a constantly-changing counter and use modulo to squeeze the result "
             "into 6 digits. Both sides run the same math, so both get the same code "
             "-- without ever sending it over the internet.",
     "code": "code = (secret + counter) % 1000000   # always 0..999999\n"
             "shown = str(code).zfill(6)            # pad to 6 digits"},
    {"heading": "Real scenario",
     "body": "2FA blocks the vast majority of account-takeover attacks. The ones "
             "that still succeed almost always involve a person being talked into "
             "sharing a code. In the lab you'll build the code generator yourself, "
             "then use it to lock NULL out.",
     "code": None},
]


# ===========================================================================
# CHALLENGES
# ===========================================================================
def _check_code(t):
    return t.ns.get("code") == 987654321 % 1000000

def _check_padded(t):
    return t.ns.get("padded") == "000042"

def _check_otp(t):
    f = t.ns.get("otp")
    if not callable(f):
        return False
    try:
        return (f(100, 5) == str((100 + 5) % 1000000).zfill(6)
                and f(999999, 2) == str((999999 + 2) % 1000000).zfill(6))
    except Exception:
        return False

def _check_valid(t):
    return t.ns.get("is_valid") is True

CHALLENGES = [
    {"title": "Squeeze a number to 6 digits",
     "goal": "A 2FA code is just a big number kept to 6 digits with modulo. Store "
             "the last 6 digits of `secret` in `code` using  secret % 1000000.",
     "seed": lambda: {"secret": 987654321},
     "intro": ["# `secret` is a big number. % 1000000 keeps the last 6 digits.",
               "# Store the 6-digit result in `code`."],
     "hint": "code = secret % 1000000",
     "solution": "code = secret % 1000000",
     "check": _check_code,
     "success": "987654321 % 1000000 is 654321 -- a 6-digit code."},
    {"title": "Pad with leading zeros",
     "goal": "A code like 42 must still show as six digits: 000042. Turn the number "
             "42 into the text \"000042\" using str(42).zfill(6) and store it in "
             "`padded`.",
     "intro": ["# str(42) makes the text '42'. .zfill(6) pads it to 6 characters.",
               "# Store '000042' in `padded`."],
     "hint": "padded = str(42).zfill(6)",
     "solution": "padded = str(42).zfill(6)",
     "check": _check_padded,
     "success": "Now short codes still look right. zfill = 'zero fill'."},
    {"title": "Build the code generator",
     "goal": "Write a function `otp(secret, counter)` that returns a 6-digit string: "
             "add secret and counter, keep 6 digits with % 1000000, and pad with "
             ".zfill(6). Test: otp(100, 5) should give '000105'.",
     "intro": ["# def otp(secret, counter):",
               "#   combine them, % 1000000, then str(...).zfill(6), and return it."],
     "hint": "def otp(secret, counter):  return str((secret + counter) % 1000000).zfill(6)",
     "solution": "def otp(secret, counter):\n"
                 "    return str((secret + counter) % 1000000).zfill(6)",
     "check": _check_otp,
     "success": "Your own authenticator! This is basically how real 2FA apps work."},
    {"title": "Verify a code",
     "goal": "Logging in checks the code you typed against the expected one. Set "
             "`is_valid` to whether `entered` equals `expected`.",
     "seed": lambda: {"entered": "418320", "expected": "418320"},
     "intro": ["# `entered` is what the user typed; `expected` is the real code.",
               "# Set `is_valid` to the True/False result of comparing them."],
     "hint": "is_valid = entered == expected",
     "solution": "is_valid = entered == expected",
     "check": _check_valid,
     "success": "A match means the user really has the device. That's the second factor."},
]


# ===========================================================================
# BOSS FIGHT  --  refuse the phish, then authenticate to lock NULL out.
# ===========================================================================
class Level8(Scene):
    def __init__(self, game):
        super().__init__(game)
        self.phase = 1                  # 1 = refuse the phish, 2 = enter the code
        # The legit 6-digit code your authenticator is showing.
        self.code = "418320"
        self.share_btn = Button(60, 320, 360, 56, "Reply with my code", color="red")
        self.refuse_btn = Button(60, 390, 360, 56, "Refuse -- never share it",
                                 color="green")
        self.box = TextInput(60, 360, 280, 56, placeholder="enter the 6-digit code",
                             max_len=6)
        self.feedback = ""
        self.won = False
        self.continue_btn = Button(WIDTH - 240, HEIGHT - 90, 200, 56, "Continue >")

    def handle_event(self, event):
        if self.phase == 1:
            if self.share_btn.handle_event(event):
                self.feedback = ("NEVER do that. A real service won't ask. (Nothing "
                                 "leaked here -- but stay sharp.)")
            if self.refuse_btn.handle_event(event):
                self.feedback = "Good. You refused the phish. Now authenticate yourself."
                self.phase = 2
        elif self.phase == 2 and not self.won:
            if self.box.handle_event(event):       # Enter pressed in the box
                if self.box.text == self.code:
                    self.won = True
                    self.feedback = ("Access approved for YOU. NULL had your password "
                                     "but not your code -- locked out!")
                else:
                    self.feedback = "That doesn't match the authenticator. Try again."
        else:
            if self.continue_btn.handle_event(event):
                self.next_scene = self.return_to

    def draw(self, surface):
        surface.fill(COLORS["bg"])
        self.draw_header(surface, "LEVEL 8  //  RELAY")

        if self.phase == 1:
            draw_text(surface, "Your phone buzzes with a message:", 60, 100,
                      size=20, color="gray")
            panel = pygame.Rect(60, 135, WIDTH - 120, 110)
            pygame.draw.rect(surface, COLORS["panel"], panel, border_radius=8)
            pygame.draw.rect(surface, COLORS["red"], panel, width=1, border_radius=8)
            draw_text(surface, "From: IT-Security (unverified)", 76, 150, size=17,
                      color="amber")
            draw_text(surface, "\"This is IT Security. We detected a login. Reply "
                      "with the 6-digit code we just sent so we can verify it's you.\"",
                      76, 178, size=18, color="white", max_width=WIDTH - 160)
            self.share_btn.draw(surface)
            self.refuse_btn.draw(surface)

        elif self.phase == 2:
            draw_text(surface, "NULL is trying to log in with your stolen password. "
                      "Your authenticator shows:", 60, 100, size=20, color="white",
                      max_width=WIDTH - 120)
            # The big code display.
            codepanel = pygame.Rect(60, 150, 300, 80)
            pygame.draw.rect(surface, COLORS["panel2"], codepanel, border_radius=8)
            draw_text(surface, self.code, 210, 168, size=46, color="green",
                      center=True)
            draw_text(surface, "Enter it to approve YOUR login and deny NULL:",
                      60, 300, size=18, color="gray")
            if not self.won:
                self.box.draw(surface)

        if self.feedback:
            draw_text(surface, self.feedback, 60, 480, size=20,
                      color="green" if self.won else "amber", max_width=WIDTH - 120)
        if self.won:
            self.continue_btn.draw(surface)
