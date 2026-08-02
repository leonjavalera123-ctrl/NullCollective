"""
engine.py  --  The reusable "toolkit" for our whole game.
=========================================================

A total-beginner note before you read on:
    pygame draws everything onto a big rectangle of pixels called a "surface".
    The main one is the window itself (we call it `screen`).
    To make anything appear you: (1) draw it, then (2) "flip"/update the screen.
    A game does this ~60 times per second inside a loop. That loop lives in main.py.

This file does NOT contain any level. It only contains *helpers* that every
level reuses, so we don't copy-paste the same code seven times:
    - COLORS:        a palette of named colors so we never juggle raw numbers
    - fonts():       loads the text fonts once
    - draw_text():   puts wrapped text on the screen
    - Button:        a clickable button
    - TextInput:     a box the player can type into
    - Scene:         the "base class" every level inherits from

Read this file first. Once you understand these tools, every level file will
feel like plain English.
"""

import pygame  # the game library we installed with: pip install pygame
import audio    # our sound helper (audio.play("click"), etc.)


# ---------------------------------------------------------------------------
# 1) THE WINDOW SIZE
# ---------------------------------------------------------------------------
# These are just numbers (variables). We give them ALL-CAPS names by convention
# to signal "this is a constant -- a setting we don't change while playing".
WIDTH = 1000   # how many pixels wide the window is
HEIGHT = 680   # how many pixels tall the window is
FPS = 60       # "frames per second" -- how many times we redraw each second


# ---------------------------------------------------------------------------
# 2) THE COLOR PALETTE
# ---------------------------------------------------------------------------
# A color in pygame is a tuple of 3 numbers: (Red, Green, Blue), each 0-255.
# (0, 0, 0) is black, (255, 255, 255) is white.
# We store them in a dictionary so we can ask for a color BY NAME, e.g.
# COLORS["green"].  A dictionary maps a "key" (the name) to a "value" (the color).
COLORS = {
    "bg":      (10, 12, 18),     # near-black background
    "panel":   (20, 24, 34),     # slightly lighter box background
    "panel2":  (28, 33, 47),     # even lighter, for nested boxes
    "green":   (57, 255, 137),   # neon "hacker" green -- our main accent
    "cyan":    (0, 200, 255),    # cyan for highlights/links
    "red":     (255, 70, 70),    # danger / enemy / wrong
    "amber":   (255, 190, 60),   # warnings
    "white":   (230, 230, 235),  # normal readable text
    "gray":    (120, 125, 140),  # dim/secondary text
    "purple":  (180, 120, 255),  # the villain NULL's color
}


# ---------------------------------------------------------------------------
# 3) FONTS
# ---------------------------------------------------------------------------
# A "font" is a typeface at a given size. Loading a font is a little slow, so we
# load each size ONCE and keep them in a dictionary to reuse. The leading
# underscore in `_FONT_CACHE` is a gentle hint: "internal, don't touch directly".
_FONT_CACHE = {}

def font(size, mono=True):
    """Return a font of the given pixel size, creating it once then reusing it.

    `mono=True` gives a monospace (typewriter) font -- every letter the same
    width -- which makes our game look like a hacker terminal.
    """
    key = (size, mono)              # the cache key: this exact size + style
    if key not in _FONT_CACHE:      # have we built this font before?
        if mono:
            # SysFont looks for a font already installed on your computer.
            # "consolas" exists on Windows; the list gives backups just in case.
            f = pygame.font.SysFont("consolas,couriernew,monospace", size)
        else:
            f = pygame.font.SysFont("segoeui,arial", size)
        _FONT_CACHE[key] = f        # store it so next time is instant
    return _FONT_CACHE[key]


# ---------------------------------------------------------------------------
# 4) DRAWING TEXT (with automatic word-wrapping)
# ---------------------------------------------------------------------------
def draw_text(surface, text, x, y, size=22, color="white",
              mono=True, max_width=None, line_gap=6, center=False):
    """Draw `text` onto `surface` starting at position (x, y).

    Pixels are measured from the TOP-LEFT corner of the window:
        x grows to the RIGHT, y grows DOWNWARD.

    If `max_width` is given, long lines wrap onto multiple lines automatically.
    Returns the y position just BELOW the text we drew, so the caller can keep
    stacking more text underneath it.
    """
    f = font(size, mono)
    # Allow either a color NAME ("green") or a raw (r, g, b) tuple.
    rgb = COLORS[color] if isinstance(color, str) else color

    # First, split the text into lines that fit inside max_width.
    if max_width is None:
        lines = text.split("\n")  # only break where the text itself has newlines
    else:
        lines = []
        for paragraph in text.split("\n"):     # respect explicit newlines too
            words = paragraph.split(" ")
            current = ""
            for word in words:
                trial = word if current == "" else current + " " + word
                # f.size(...) tells us how wide a string would be in pixels.
                if f.size(trial)[0] <= max_width:
                    current = trial            # still fits -- keep adding words
                else:
                    lines.append(current)      # full -- start a new line
                    current = word
            lines.append(current)

    # Now actually render each line, moving down by the line height each time.
    line_height = f.get_height() + line_gap
    for i, line in enumerate(lines):
        img = f.render(line, True, rgb)        # turn the string into a picture
        rect = img.get_rect()                  # a rectangle the size of that picture
        if center:
            rect.midtop = (x, y + i * line_height)   # x is the CENTER
        else:
            rect.topleft = (x, y + i * line_height)  # x is the LEFT edge
        surface.blit(img, rect)                # "blit" = paste the picture on
    return y + len(lines) * line_height        # bottom edge, for stacking


# ---------------------------------------------------------------------------
# 5) A CLICKABLE BUTTON
# ---------------------------------------------------------------------------
class Button:
    """A rectangle with a label that knows when it has been clicked.

    A "class" is a blueprint. From it we make many "objects" (actual buttons),
    each remembering its own position, label, and colors. `self` always means
    "this particular button".
    """

    def __init__(self, x, y, w, h, label, color="green", text_color="white"):
        # __init__ runs once when we create a button. It stores the settings.
        self.rect = pygame.Rect(x, y, w, h)   # a Rect bundles x, y, width, height
        self.label = label
        self.color = color
        self.text_color = text_color
        self.hover = False                    # is the mouse currently over it?
        self.enabled = True                   # disabled buttons can't be clicked

    def handle_event(self, event):
        """Look at one input event. Return True only if THIS button was clicked."""
        if event.type == pygame.MOUSEMOTION:
            # event.pos is the mouse (x, y). .collidepoint asks "is it inside me?"
            now_over = self.rect.collidepoint(event.pos)
            # Play a soft blip only when the mouse FIRST enters the button.
            if now_over and not self.hover and self.enabled:
                audio.play("hover")
            self.hover = now_over
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.enabled and self.rect.collidepoint(event.pos):
                audio.play("click")           # a satisfying click
                return True                   # yes! a left-click landed on us
        return False                          # otherwise, not clicked

    def draw(self, surface):
        base = COLORS[self.color] if isinstance(self.color, str) else self.color
        if not self.enabled:
            base = COLORS["gray"]             # show disabled buttons as gray
        # Fill the button. When hovered, draw a solid fill; otherwise an outline.
        if self.hover and self.enabled:
            pygame.draw.rect(surface, base, self.rect, border_radius=8)
            txt_color = COLORS["bg"]          # dark text on the bright fill
        else:
            pygame.draw.rect(surface, COLORS["panel2"], self.rect, border_radius=8)
            pygame.draw.rect(surface, base, self.rect, width=2, border_radius=8)
            txt_color = base
        # Center the label inside the button.
        f = font(22)
        img = f.render(self.label, True, txt_color)
        surface.blit(img, img.get_rect(center=self.rect.center))


# ---------------------------------------------------------------------------
# 6) A TEXT INPUT BOX (so the player can type)
# ---------------------------------------------------------------------------
class TextInput:
    """A box that collects typed characters. Used for passwords, answers, etc."""

    def __init__(self, x, y, w, h, placeholder="", max_len=40, mask=False):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = ""                 # what the player has typed so far
        self.placeholder = placeholder # faint hint shown when empty
        self.max_len = max_len         # don't let the string grow forever
        self.mask = mask               # if True, show **** instead (for passwords)
        self.active = True             # is this box currently receiving keys?

    def handle_event(self, event):
        """Update the typed text. Return True when the player presses Enter."""
        if event.type == pygame.MOUSEBUTTONDOWN:
            # Click inside to focus, click outside to unfocus.
            self.active = self.rect.collidepoint(event.pos)
        elif event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_RETURN:        # the Enter key
                return True                         # signal "submitted!"
            elif event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]          # drop the last character
            elif len(self.text) < self.max_len and event.unicode.isprintable():
                self.text += event.unicode          # add the typed character
        return False

    def draw(self, surface):
        border = COLORS["green"] if self.active else COLORS["gray"]
        pygame.draw.rect(surface, COLORS["panel"], self.rect, border_radius=6)
        pygame.draw.rect(surface, border, self.rect, width=2, border_radius=6)
        # Decide what string to show.
        if self.text:
            shown = ("*" * len(self.text)) if self.mask else self.text
            color = "white"
        else:
            shown = self.placeholder                # nothing typed yet
            color = "gray"
        f = font(24)
        img = f.render(shown, True, COLORS[color])
        # Vertically center the text, with a little left padding.
        surface.blit(img, (self.rect.x + 12, self.rect.centery - img.get_height() // 2))


# ---------------------------------------------------------------------------
# 7) THE SCENE "BASE CLASS"
# ---------------------------------------------------------------------------
class Scene:
    """Every screen in the game (menu, each level, win screen) is a Scene.

    A Scene promises three abilities. The game loop in main.py calls them every
    frame: handle_event (react to input), update (advance time/animation), and
    draw (paint the screen). Levels INHERIT from this and override these methods.

    To move to another scene, a level sets `self.next_scene = "some_name"`.
    main.py notices that and swaps scenes for us.
    """

    def __init__(self, game):
        self.game = game            # a reference back to the main Game object
        self.next_scene = None      # stays None until we want to switch scenes
        # Where a boss should go when it's beaten. main.py sets this when it
        # builds the level, so bosses don't hardcode their own debrief number --
        # that's what lets us reorder and insert levels freely.
        self.return_to = None

    def handle_event(self, event):
        """React to one input event (key press, mouse click). Override me."""
        pass

    def update(self, dt):
        """Advance animations. `dt` = seconds since last frame. Override me."""
        pass

    def draw(self, surface):
        """Paint everything for this frame. Override me."""
        pass

    # A small shared helper so every scene can draw the same title bar look.
    def draw_header(self, surface, title, subtitle=""):
        pygame.draw.rect(surface, COLORS["panel"], (0, 0, WIDTH, 70))
        pygame.draw.line(surface, COLORS["green"], (0, 70), (WIDTH, 70), 2)
        draw_text(surface, title, 24, 14, size=30, color="green")
        if subtitle:
            draw_text(surface, subtitle, WIDTH - 24, 26, size=18,
                      color="gray", center=False)
