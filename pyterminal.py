"""
pyterminal.py  --  a REAL, working Python interpreter you can type into.
========================================================================

This is the centerpiece of the learning side of the game. It behaves like the
Python prompt you'd get by typing `python` in a real terminal:

    >>> 2 + 2
    4
    >>> name = "vigilante"
    >>> print("hi", name)
    hi vigilante

It supports:
    - single lines (expressions show their value, like a real REPL)
    - multi-line blocks (for-loops, if, def...): a line ending with ':' starts a
      block; keep typing; press Enter on a BLANK line to run it
    - friendly error messages (so a typo teaches instead of scaring you)
    - command history with the Up / Down arrow keys
    - Tab inserts 4 spaces (Python uses indentation for blocks)

How it actually runs your code (the important part):
    Python can turn text into a runnable "code object" with compile(), then run
    it with eval() (for expressions, which produce a value) or exec() (for
    statements, which DO something). We capture anything you print() and show it.
    The variables you create live in a dictionary called the "namespace" -- that's
    literally how Python tracks names like `x` -> 5.

NOTE: this runs real Python on your machine. It's meant for learning; type the
challenge code, experiment freely, and read the errors -- they're your friend.
"""

import io
import copy
import contextlib
import pygame
import audio
from engine import font, draw_text, COLORS


class PyTerminal:
    def __init__(self, rect, seed=None, intro=None):
        """rect = where to draw (a pygame.Rect).
           seed = a dict of variables to pre-load (the level's data).
           intro = list of grey welcome lines to print at the top."""
        self.rect = rect
        # The "namespace": a dictionary mapping variable names -> values. We hand
        # it to exec/eval so the player's variables persist between commands.
        self.ns = {}
        if seed:
            self.ns.update(seed)            # pre-load level data (e.g. a wordlist)

        # The scrollback: a list of (text, color_name) pairs we've printed.
        self.lines = []
        if intro:
            for ln in intro:
                self.lines.append((ln, "gray"))

        self.input = ""                     # what the player is currently typing
        self.block = []                     # accumulated lines of a multi-line block
        self.history = []                   # past commands, for the Up/Down keys
        self.hist_pos = None                # where we are while browsing history
        self.scroll = 0                     # how many lines scrolled up from bottom
        self.cursor_on = True               # blinking cursor state
        self.cursor_timer = 0.0
        self.last_run = ""                  # text produced by the most recent run
        self.font_size = 18

        # Remember the STARTING state so a "Clear" button can restore it. We keep
        # a deep copy so that editing variables later doesn't change the snapshot.
        try:
            self._seed_snapshot = copy.deepcopy(seed) if seed else {}
        except Exception:
            self._seed_snapshot = dict(seed) if seed else {}
        self._intro = list(intro) if intro else []

    def reset(self):
        """Wipe the screen and restore the starting variables -- a fresh start."""
        try:
            self.ns = copy.deepcopy(self._seed_snapshot)
        except Exception:
            self.ns = dict(self._seed_snapshot)
        self.lines = [(ln, "gray") for ln in self._intro]
        self.lines.append(("# screen cleared -- fresh start.", "gray"))
        self.input = ""
        self.block = []
        self.history = []
        self.hist_pos = None
        self.scroll = 0
        self.last_run = ""

    # -- a tiny helper to add text (possibly multi-line) to the scrollback --
    def echo(self, text, color="white"):
        for ln in str(text).split("\n"):
            self.lines.append((ln, color))
        # Keep the scrollback from growing forever.
        if len(self.lines) > 400:
            self.lines = self.lines[-400:]

    @property
    def in_block(self):
        return len(self.block) > 0

    def run_source(self, source):
        """Compile and run one complete piece of code, capturing its output."""
        self.last_run = ""
        buffer = io.StringIO()              # a fake "screen" to capture print()
        try:
            # Try to treat it as an EXPRESSION first (something with a value).
            try:
                code = compile(source, "<lab>", "eval")
                is_expr = True
            except SyntaxError:
                # Not an expression -> treat it as STATEMENTS (a loop, assignment...).
                code = compile(source, "<lab>", "exec")
                is_expr = False

            # contextlib.redirect_stdout sends every print() into our buffer.
            with contextlib.redirect_stdout(buffer):
                if is_expr:
                    result = eval(code, self.ns)
                else:
                    exec(code, self.ns)
                    result = None

            printed = buffer.getvalue()
            if printed:
                self.echo(printed.rstrip("\n"), "white")
            # In a REPL, a bare expression shows its value (e.g. typing 2+2 -> 4).
            if is_expr and result is not None:
                self.echo(repr(result), "cyan")
            self.last_run = printed + ("" if result is None else repr(result))

        except Exception as e:
            # Show a short, friendly error: the TYPE and the message. Reading these
            # is one of the most valuable coding skills there is.
            self.echo(f"{type(e).__name__}: {e}", "red")
            self.last_run = f"{type(e).__name__}: {e}"
            audio.play("error")             # a gentle buzz to flag the mistake

    def submit_line(self):
        """Called when the player presses Enter. Decides: run now, or keep typing?"""
        line = self.input
        # Echo what they typed, with the right prompt.
        prompt = "... " if self.in_block else ">>> "
        self.echo(prompt + line, "green")

        if self.in_block:
            # We're inside a multi-line block. A blank line means "run it now".
            if line.strip() == "":
                source = "\n".join(self.block)
                self.block = []
                self.history.append(source)
                self.run_source(source)
            else:
                self.block.append(line)
        else:
            if line.strip() == "":
                pass                                    # empty line, do nothing
            elif line.rstrip().endswith(":"):
                # Starts a block (for/if/def...). Begin collecting lines.
                self.block.append(line)
            else:
                self.history.append(line)
                self.run_source(line)

        self.input = ""
        self.hist_pos = None
        self.scroll = 0                                 # snap view back to bottom

    def handle_event(self, event):
        if event.type != pygame.KEYDOWN:
            # Mouse wheel scrolls the history up/down.
            if event.type == pygame.MOUSEWHEEL:
                self.scroll = max(0, self.scroll + event.y)
            return

        if event.key == pygame.K_RETURN:
            self.submit_line()
        elif event.key == pygame.K_BACKSPACE:
            self.input = self.input[:-1]
        elif event.key == pygame.K_TAB:
            self.input += "    "                        # 4 spaces = one indent level
        elif event.key == pygame.K_UP:
            self._recall_history(-1)
        elif event.key == pygame.K_DOWN:
            self._recall_history(+1)
        elif event.unicode and event.unicode.isprintable():
            self.input += event.unicode

    def _recall_history(self, direction):
        """Walk through past commands with the arrow keys."""
        if not self.history:
            return
        if self.hist_pos is None:
            self.hist_pos = len(self.history)
        self.hist_pos = max(0, min(len(self.history), self.hist_pos + direction))
        if self.hist_pos >= len(self.history):
            self.input = ""
        else:
            # Only recall the first line of a multi-line block, to keep it simple.
            self.input = self.history[self.hist_pos].split("\n")[0]

    def update(self, dt):
        # Blink the cursor about twice a second.
        self.cursor_timer += dt
        if self.cursor_timer > 0.5:
            self.cursor_timer = 0
            self.cursor_on = not self.cursor_on

    def draw(self, surface):
        # The terminal panel.
        pygame.draw.rect(surface, (6, 8, 12), self.rect, border_radius=8)
        pygame.draw.rect(surface, COLORS["green"], self.rect, width=1, border_radius=8)

        f = font(self.font_size)
        line_h = f.get_height() + 2
        pad = 12
        max_w = self.rect.width - pad * 2

        # Word-wrap every scrollback line to the panel width.
        wrapped = []                        # list of (text, color)
        for text, color in self.lines:
            for piece in self._wrap(text, f, max_w):
                wrapped.append((piece, color))

        # Build the current input line(s) with the proper prompt.
        prompt = "... " if self.in_block else ">>> "
        cursor = "_" if self.cursor_on else " "
        input_render = prompt + self.input + cursor
        input_wrapped = self._wrap(input_render, f, max_w) or [input_render]

        # Figure out how many lines fit, and show the bottom-most ones.
        usable_h = self.rect.height - pad * 2
        visible = max(1, usable_h // line_h)
        all_lines = wrapped + [(t, "green") for t in input_wrapped]
        # Apply scroll: 0 = bottom. Larger = further up.
        end = len(all_lines) - self.scroll
        start = max(0, end - visible)
        view = all_lines[start:end]

        y = self.rect.y + pad
        for text, color in view:
            draw_text(surface, text, self.rect.x + pad, y, size=self.font_size,
                      color=color)
            y += line_h

    def _wrap(self, text, f, max_w):
        """Break one string into pieces that each fit within max_w pixels."""
        if f.size(text)[0] <= max_w:
            return [text]
        pieces = []
        current = ""
        for ch in text:
            if f.size(current + ch)[0] <= max_w:
                current += ch
            else:
                pieces.append(current)
                current = ch
        if current:
            pieces.append(current)
        return pieces
