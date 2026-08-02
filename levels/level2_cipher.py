"""
LEVEL 2  --  CIPHER   (Cryptography: the Caesar cipher)
=======================================================

Security idea you learn:
    A "cipher" scrambles a message so only someone with the key can read it.
    The Caesar cipher shifts every letter forward in the alphabet by a fixed
    amount (the "key"). Shift 'A' by 3 and you get 'D'. It's ancient and weak --
    there are only 25 shifts to try -- which is exactly why YOU can crack it.

Python you learn:
    - writing and calling a function with parameters
    - ord(letter) -> a number, chr(number) -> a letter  (letters ARE numbers!)
    - the modulo operator %  to "wrap around" Z back to A
    - building a new string letter by letter

How the level plays:
    NULL's intercepted order is scrambled. Turn the SHIFT dial with the arrow
    keys (or buttons) until the preview becomes readable English, then decrypt.
"""

import pygame
from engine import Scene, Button, draw_text, COLORS, WIDTH, HEIGHT


# ===========================================================================
# INTEL  --  what Cipher does, and the Python behind it.
# ===========================================================================
INTEL = [
    {
        "heading": "What Cipher does",
        "body": "Cipher scrambles NULL's orders so only the gang can read them. "
                "Their favorite is the Caesar cipher: shift every letter forward "
                "in the alphabet by a secret number (the 'key'). Shift by 3 and "
                "A->D, B->E, and so on. Here is encryption in a few lines:",
        "code": "for ch in message:\n"
                "    code = (ord(ch) - ord('A') + key) % 26\n"
                "    secret += chr(code + ord('A'))",
    },
    {
        "heading": "The trick: letters ARE numbers",
        "body": "Every character has a number. ord('A') is 65, ord('B') is 66... "
                "chr() turns the number back into a letter. The % (modulo) operator "
                "gives the remainder of a division -- perfect for 'wrapping' Z back "
                "around to A so the alphabet forms a loop.",
        "code": "ord('A')   -> 65\n"
                "chr(66)    -> 'B'\n"
                "25 % 26    -> 25      (Z stays Z)\n"
                "26 % 26    -> 0       (one past Z wraps to A)",
    },
    {
        "heading": "Why YOU can break it",
        "body": "A Caesar cipher has only 25 possible keys. A defender just tries "
                "all of them and reads whichever output is English -- that's the "
                "boss fight. Real encryption (like AES) uses keys so enormous that "
                "trying them all would outlast the universe. In the lab you'll "
                "build the cipher itself.",
        "code": None,
    },
]


# ===========================================================================
# CHALLENGES
# ===========================================================================
def _check_ordn(t):
    return t.ns.get("n") == ord("H")          # 72

def _check_wrap(t):
    return t.ns.get("shifted") == "a"

def _check_enc(t):
    f = t.ns.get("enc")
    if not callable(f):
        return False
    try:
        # A correct Caesar function shifts and wraps around the alphabet.
        return f("ABC", 1) == "BCD" and f("XYZ", 3) == "ABC"
    except Exception:
        return False

def _check_next(t):
    return t.ns.get("nxt") == "B"

def _check_back(t):
    return t.ns.get("dec") == "A"

CHALLENGES = [
    {
        "title": "Letters are numbers",
        "goal": "Use ord() to get the number for the capital letter 'H' and store "
                "it in a variable named `n`. Then try chr(n) to turn it back.",
        "intro": ["# Try:  ord('H')   then store it:  n = ord('H')"],
        "hint": "Type:  n = ord('H')   then press Enter. Check it with  n  or  chr(n).",
        "solution": "n = ord('H')",
        "check": _check_ordn,
        "success": "ord('H') is 72. Letters and numbers are two views of the same thing.",
    },
    {
        "title": "Shift one letter forward",
        "goal": "Encrypting is just shifting. Get the letter that comes right after "
                "'A' (which is 'B') by adding 1 to its number, and store it in `nxt`. "
                "Use chr() and ord() together.",
        "intro": ["# ord('A') is 65. Add 1, then turn it back with chr().",
                  "# Store the result ('B') in a variable named `nxt`."],
        "hint": "nxt = chr(ord('A') + 1)",
        "solution": "nxt = chr(ord('A') + 1)",
        "check": _check_next,
        "success": "'A' shifted forward by 1 is 'B'. That's encryption in miniature.",
    },
    {
        "title": "Shift one letter back",
        "goal": "Decrypting shifts the other way. The variable `c` holds 'D'. Shift "
                "it back by 3 to recover 'A' and store it in `dec`.",
        "seed": lambda: {"c": "D"},
        "intro": ["# `c` = 'D'. Subtract 3 from its number, then chr() it back.",
                  "# Store the recovered letter ('A') in `dec`."],
        "hint": "dec = chr(ord(c) - 3)",
        "solution": "dec = chr(ord(c) - 3)",
        "check": _check_back,
        "success": "'D' shifted back 3 is 'A' -- you just decrypted a single letter.",
    },
    {
        "title": "Wrap around the alphabet",
        "goal": "Shift the letter 'z' forward by 1 so it wraps to 'a'. Use the "
                "modulo formula and store the resulting letter in `shifted`.",
        "intro": ["# Shift 'z' by 1 and wrap Z->A using % 26.",
                  "# Formula:  chr((ord('z') - ord('a') + 1) % 26 + ord('a'))"],
        "hint": "shifted = chr((ord('z') - ord('a') + 1) % 26 + ord('a'))",
        "solution": "shifted = chr((ord('z') - ord('a') + 1) % 26 + ord('a'))",
        "check": _check_wrap,
        "success": "'z' wrapped to 'a'. That % 26 is what makes the alphabet a circle.",
    },
    {
        "title": "Build the cipher",
        "goal": "Write a function named `enc(text, key)` that returns `text` with "
                "each UPPERCASE letter Caesar-shifted by `key`. Test: enc('ABC', 1) "
                "should give 'BCD', and enc('XYZ', 3) should give 'ABC'.",
        "intro": ["# Define a function:  def enc(text, key):",
                  "#   build a result string letter by letter and return it.",
                  "# Assume input is uppercase A-Z."],
        "hint": "def enc(text, key):  /  out = ''  /  for ch in text:  /  "
                "out += chr((ord(ch)-65+key)%26 + 65)  /  return out",
        "solution": "def enc(text, key):\n    out = ''\n    for ch in text:\n"
                    "        out += chr((ord(ch) - 65 + key) % 26 + 65)\n    return out",
        "check": _check_enc,
        "success": "You wrote a working Caesar cipher -- the same one Cipher uses.",
    },
]


def caesar(text, shift):
    """Shift every letter in `text` by `shift` places. Non-letters pass through.

    This single function can BOTH encrypt (positive shift) and decrypt
    (negative shift). Read it slowly -- it's the heart of the level.
    """
    result = ""                          # we'll build the answer here
    for ch in text:                      # look at each character one at a time
        if ch.isalpha():                 # only shift A-Z / a-z, leave spaces etc.
            # Pick the right "base": 'A' (65) for uppercase, 'a' (97) for lowercase.
            base = ord("A") if ch.isupper() else ord("a")
            # Steps:
            #   ord(ch) - base   -> turn the letter into 0..25
            #   + shift          -> move it
            #   % 26             -> wrap around so 'Z'+1 becomes 'A'
            #   + base           -> turn 0..25 back into a real letter code
            #   chr(...)         -> turn the number back into a character
            offset = (ord(ch) - base + shift) % 26
            result += chr(base + offset)
        else:
            result += ch                 # keep spaces, punctuation as-is
    return result


# The hidden order from NULL. We encrypt it with a SECRET shift the player must find.
PLAINTEXT = "STRIKE THE CENTRAL BANK AT MIDNIGHT"
SECRET_SHIFT = 7
CIPHERTEXT = caesar(PLAINTEXT, SECRET_SHIFT)   # what the player actually sees


class Level2(Scene):
    def __init__(self, game):
        super().__init__(game)
        # The player's CURRENT guess at the shift. To DECRYPT we apply the
        # opposite shift, so trying shift = SECRET_SHIFT reveals the message.
        self.guess = 0
        self.won = False
        self.left_btn = Button(60, 470, 150, 56, "< Shift -")
        self.right_btn = Button(230, 470, 150, 56, "Shift + >")
        self.continue_btn = Button(WIDTH - 240, HEIGHT - 90, 200, 56, "Continue >")

    def current_preview(self):
        """Decrypt the ciphertext using the player's current guess."""
        # Decrypting with guess `g` means shifting back by `g` (a NEGATIVE shift).
        return caesar(CIPHERTEXT, -self.guess)

    def handle_event(self, event):
        # Arrow keys are a nice, tactile way to turn the dial.
        if event.type == pygame.KEYDOWN and not self.won:
            if event.key in (pygame.K_LEFT, pygame.K_DOWN):
                self.guess = (self.guess - 1) % 26
            elif event.key in (pygame.K_RIGHT, pygame.K_UP):
                self.guess = (self.guess + 1) % 26
        # Buttons do the same thing for mouse players.
        if not self.won:
            if self.left_btn.handle_event(event):
                self.guess = (self.guess - 1) % 26
            if self.right_btn.handle_event(event):
                self.guess = (self.guess + 1) % 26
        if self.won and self.continue_btn.handle_event(event):
            self.next_scene = self.return_to

    def update(self, dt):
        # You win the instant your decryption matches the real message.
        if self.current_preview() == PLAINTEXT:
            self.won = True

    def draw(self, surface):
        surface.fill(COLORS["bg"])
        self.draw_header(surface, "LEVEL 2  //  CIPHER")

        draw_text(surface, "Intercepted, encrypted order from NULL:",
                  60, 100, size=20, color="gray")
        # The scrambled message in a panel.
        panel = pygame.Rect(60, 135, WIDTH - 120, 70)
        pygame.draw.rect(surface, COLORS["panel"], panel, border_radius=8)
        draw_text(surface, CIPHERTEXT, WIDTH // 2, 160, size=28,
                  color="red", center=True)

        # The dial readout.
        draw_text(surface, f"SHIFT DIAL:  {self.guess}", 60, 240, size=24,
                  color="amber")
        draw_text(surface, "(use LEFT / RIGHT arrow keys, or the buttons below)",
                  60, 275, size=16, color="gray")

        # Live decrypted preview -- turns green when it's real English.
        draw_text(surface, "Decryption preview:", 60, 330, size=20, color="gray")
        preview = self.current_preview()
        preview_color = "green" if self.won else "cyan"
        panel2 = pygame.Rect(60, 365, WIDTH - 120, 70)
        pygame.draw.rect(surface, COLORS["panel2"], panel2, border_radius=8)
        draw_text(surface, preview, WIDTH // 2, 390, size=28,
                  color=preview_color, center=True)

        if not self.won:
            self.left_btn.draw(surface)
            self.right_btn.draw(surface)
        else:
            draw_text(surface, f"DECRYPTED! The secret shift was {SECRET_SHIFT}.",
                      60, 470, size=24, color="green")
            draw_text(surface, "Target exposed. The bank has been warned.",
                      60, 505, size=20, color="white")
            # If the player wrote enc() in the lab, run it to prove their own code
            # reproduces NULL's cipher with this key.
            enc = self.game.toolkit.get("enc")
            if callable(enc):
                try:
                    sample = enc("HELLO", SECRET_SHIFT)
                    draw_text(surface, "Powered by your Lab code:  "
                              f"enc(\"HELLO\", {SECRET_SHIFT})  ->  \"{sample}\"",
                              60, 540, size=18, color="cyan")
                except Exception:
                    pass
            self.continue_btn.draw(surface)
