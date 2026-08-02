"""
labscene.py  --  two reusable scenes that turn each level into a Python lesson.
===============================================================================

IntelScene  -- a "what is the hacker doing?" briefing. It pages through sections
               of explanation, each with optional example code shown the way an
               attacker would actually write it.

LabScene    -- the hands-on part. It hosts a real PyTerminal and walks the player
               through a list of coding CHALLENGES. Each challenge has a goal, a
               hint, a solution, and a checker that watches what you type and
               lights up green when you've done it.

Both are DATA-DRIVEN: the words and challenges live in each level file, and these
classes just present them. Write the presentation once, reuse it seven times.
"""

import pygame
import audio
from engine import Scene, Button, draw_text, COLORS, WIDTH, HEIGHT
from pyterminal import PyTerminal
from effects import MatrixRain


def _make_dim(alpha):
    """A reusable translucent dark sheet to lay over the matrix rain so text on
    top stays readable. alpha: 0 = clear, 255 = solid black-ish."""
    s = pygame.Surface((WIDTH, HEIGHT))
    s.fill(COLORS["bg"])
    s.set_alpha(alpha)
    return s


class IntelScene(Scene):
    """A paged information screen, shown one section at a time.

    It is reused for TWO things by passing different text and styling:
      - the INTEL briefing (what the hacker does) -- red 'attacker' code style
      - the PYTHON LESSON  (the code, slowly)     -- green 'example' code style
    Reusing one class for both keeps the game small and consistent.
    """

    def __init__(self, game, level_no, header, sections, target,
                 code_label="// example:", accent="red", final_label="Next >"):
        super().__init__(game)
        self.level_no = level_no
        self.header = header            # e.g. "INTEL: GHOST" or "PYTHON LESSON"
        self.sections = sections        # list of {heading, body, code}
        self.target = target            # where to go after the last section
        self.code_label = code_label    # the little label above each code box
        self.accent = accent            # color name for the code box border/label
        self.final_label = final_label  # what the Next button says on the last page
        self.page = 0
        self.next_btn = Button(WIDTH - 260, HEIGHT - 80, 220, 52, "Next >")
        self.back_btn = Button(40, HEIGHT - 80, 160, 52, "< Back", color="gray")
        # Faint falling-code background.
        self.rain = MatrixRain(WIDTH, HEIGHT)
        self.dim = _make_dim(210)

    def handle_event(self, event):
        if self.next_btn.handle_event(event):
            self.page += 1
            if self.page >= len(self.sections):
                self.next_scene = self.target          # done reading -> move on
        if self.back_btn.handle_event(event) and self.page > 0:
            self.page -= 1

    def update(self, dt):
        self.rain.update(dt)

    def draw(self, surface):
        surface.fill(COLORS["bg"])
        self.rain.draw(surface)
        surface.blit(self.dim, (0, 0))
        self.draw_header(surface, f"LEVEL {self.level_no}  //  {self.header}")

        sec = self.sections[self.page]
        draw_text(surface, sec["heading"], 50, 92, size=28, color="amber")
        y = draw_text(surface, sec["body"], 50, 140, size=21, color="white",
                      max_width=WIDTH - 100, line_gap=7)

        # If this section includes example code, show it in a code panel.
        if sec.get("code"):
            y += 18
            code_lines = sec["code"].split("\n")
            panel_h = len(code_lines) * 26 + 50
            panel = pygame.Rect(50, y, WIDTH - 100, panel_h)
            pygame.draw.rect(surface, (6, 8, 12), panel, border_radius=8)
            pygame.draw.rect(surface, COLORS[self.accent], panel, width=1,
                             border_radius=8)
            draw_text(surface, self.code_label, 66, y + 12, size=15,
                      color=self.accent)
            cy = y + 40
            for cl in code_lines:
                draw_text(surface, cl, 66, cy, size=18, color="cyan")
                cy += 26

        # Page indicator, e.g. "2 / 3".
        draw_text(surface, f"{self.page + 1} / {len(self.sections)}",
                  WIDTH // 2, HEIGHT - 66, size=18, color="gray", center=True)
        self.next_btn.label = (self.final_label
                               if self.page == len(self.sections) - 1 else "Next >")
        self.next_btn.draw(surface)
        if self.page > 0:
            self.back_btn.draw(surface)


class LabScene(Scene):
    """Hosts the Python terminal and steps through coding challenges."""

    def __init__(self, game, level_no, topic, challenges, target,
                 final_label="Start boss fight >"):
        super().__init__(game)
        self.level_no = level_no
        self.topic = topic
        self.challenges = challenges
        self.target = target            # the boss level to start after the lab
        self.final_label = final_label  # what the last "Next" button says
        self.idx = 0
        self.solved = False
        self.show_hint = False
        self.show_solution = False
        # This scene types into a terminal, so the global 'm'=mute shortcut must
        # NOT fire here (you need to type the letter m). Mute via the corner button.
        self.captures_text = True
        # Buttons along the bottom.
        self.hint_btn = Button(40, HEIGHT - 56, 120, 44, "Hint", color="amber")
        self.sol_btn = Button(170, HEIGHT - 56, 185, 44, "Show solution", color="gray")
        self.skip_btn = Button(365, HEIGHT - 56, 90, 44, "Skip", color="gray")
        # "Clear" wipes the terminal and restores this challenge's starting data.
        self.clear_btn = Button(465, HEIGHT - 56, 120, 44, "Clear", color="cyan")
        self.next_btn = Button(WIDTH - 230, HEIGHT - 56, 190, 44, "Next >",
                               color="green")
        # Faint falling-code background. The terminal panel sits on top of it, so
        # it only peeks through the margins -- atmosphere without distraction.
        self.rain = MatrixRain(WIDTH, HEIGHT)
        self.dim = _make_dim(220)
        self.start_challenge()

    def start_challenge(self):
        """Set up the terminal freshly for the current challenge."""
        self.solved = False
        self.show_hint = False
        self.show_solution = False
        ch = self.challenges[self.idx]
        # `seed` may be a dict or a function that returns one (for fresh data).
        seed = ch.get("seed")
        if callable(seed):
            seed = seed()
        intro = ["# Python Lab -- type code and press Enter.",
                 "# Tab = indent, Up/Down = history. Experiment freely!"]
        intro += ch.get("intro", [])
        self.term = PyTerminal(pygame.Rect(40, 250, WIDTH - 80, HEIGHT - 320),
                               seed=seed, intro=intro)

    def advance(self):
        """Move to the next challenge, or leave the lab for the boss fight."""
        # Carry any functions the player defined into the shared toolkit, so the
        # boss fight can actually run the code they just wrote.
        for fname, value in self.term.ns.items():
            if callable(value) and not fname.startswith("__"):
                self.game.toolkit[fname] = value
        self.idx += 1
        if self.idx >= len(self.challenges):
            self.next_scene = self.target
        else:
            self.start_challenge()

    def handle_event(self, event):
        # The terminal gets first crack at typing/scrolling.
        self.term.handle_event(event)
        if self.hint_btn.handle_event(event):
            self.show_hint = not self.show_hint
        if self.sol_btn.handle_event(event):
            self.show_solution = not self.show_solution
        if self.skip_btn.handle_event(event):
            self.advance()
        if self.clear_btn.handle_event(event):
            self.term.reset()           # wipe screen, restore this challenge's data
        if self.solved and self.next_btn.handle_event(event):
            self.advance()

    def update(self, dt):
        self.rain.update(dt)
        self.term.update(dt)
        if not self.solved:
            # Ask this challenge's checker whether the goal has been met.
            check = self.challenges[self.idx].get("check")
            try:
                if check and check(self.term):
                    self.solved = True
                    audio.play("success")   # reward chime the moment it's correct
            except Exception:
                pass                       # a half-typed attempt may error; ignore

    def draw(self, surface):
        surface.fill(COLORS["bg"])
        self.rain.draw(surface)
        surface.blit(self.dim, (0, 0))
        self.draw_header(surface, f"LEVEL {self.level_no}  //  LAB: {self.topic}")

        ch = self.challenges[self.idx]
        draw_text(surface, f"Challenge {self.idx + 1} / {len(self.challenges)}:  "
                  f"{ch['title']}", 40, 84, size=22, color="green")
        draw_text(surface, ch["goal"], 40, 116, size=19, color="white",
                  max_width=WIDTH - 80, line_gap=5)

        # The info strip just above the terminal: success / hint / solution.
        if self.solved:
            draw_text(surface, "SOLVED!  " + ch.get("success", "Nice work."),
                      40, 210, size=20, color="green", max_width=WIDTH - 80)
        elif self.show_solution:
            draw_text(surface, "Solution:  " + ch.get("solution", ""),
                      40, 200, size=17, color="cyan", max_width=WIDTH - 80)
        elif self.show_hint:
            draw_text(surface, "Hint:  " + ch.get("hint", ""),
                      40, 210, size=17, color="amber", max_width=WIDTH - 80)

        self.term.draw(surface)

        # Buttons.
        self.hint_btn.draw(surface)
        self.sol_btn.draw(surface)
        self.skip_btn.draw(surface)
        self.clear_btn.draw(surface)
        if self.solved:
            self.next_btn.label = (self.final_label
                                   if self.idx == len(self.challenges) - 1
                                   else "Next challenge >")
            self.next_btn.draw(surface)
