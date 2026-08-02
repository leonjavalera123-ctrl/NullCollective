"""
bosses.py  --  reusable, DATA-DRIVEN boss fights.
=================================================

Hand-writing a unique boss screen for all ~30 levels would be a mountain of
code. Instead, most levels reuse one of these two generic bosses and just feed
it DATA. Adding a level becomes "write some data", not "write a new screen".

QuizBoss  -- a "field test": answer multiple-choice questions about the topic.
FlagBoss  -- a "threat hunt": flag the bad items in a list, then scan to check.

Both follow the same contract as the hand-made bosses: when beaten, they set
self.next_scene = self.return_to (main.py fills return_to in with the right
debrief screen), so they slot into the level flow exactly like the others.
"""

import pygame
from engine import Scene, Button, draw_text, COLORS, WIDTH, HEIGHT


class QuizBoss(Scene):
    """Multiple-choice 'field test'.

    data = {
        "prompt": "one line of setup shown under the header",
        "rounds": [ {"q": "...", "options": [..4..], "answer": index}, ... ],
        "win":    "message shown when all answered correctly",
    }
    """

    def __init__(self, game, data, title):
        super().__init__(game)
        self.data = data
        self.title = title
        self.round = 0
        self.feedback = ""
        self.won = False
        self.option_btns = []
        self.build_buttons()
        self.continue_btn = Button(WIDTH - 240, HEIGHT - 80, 200, 52, "Continue >")

    def build_buttons(self):
        self.option_btns = []
        if self.round >= len(self.data["rounds"]):
            return
        for i, text in enumerate(self.data["rounds"][self.round]["options"]):
            self.option_btns.append(
                Button(60, 250 + i * 64, WIDTH - 120, 56, text, color="cyan"))

    def handle_event(self, event):
        if self.won:
            if self.continue_btn.handle_event(event):
                self.next_scene = self.return_to
            return
        for i, btn in enumerate(self.option_btns):
            if btn.handle_event(event):
                if i == self.data["rounds"][self.round]["answer"]:
                    self.feedback = "Correct!"
                    self.round += 1
                    if self.round >= len(self.data["rounds"]):
                        self.won = True
                    else:
                        self.build_buttons()
                else:
                    self.feedback = "Not quite -- think it through and try again."

    def draw(self, surface):
        surface.fill(COLORS["bg"])
        self.draw_header(surface, self.title)
        draw_text(surface, self.data.get("prompt", ""), 60, 88, size=18,
                  color="gray", max_width=WIDTH - 120)

        if self.won:
            draw_text(surface, self.data.get("win", "Field test passed!"),
                      60, 240, size=24, color="green", max_width=WIDTH - 120)
            self.continue_btn.draw(surface)
            return

        total = len(self.data["rounds"])
        draw_text(surface, f"Question {self.round + 1} / {total}", 60, 150,
                  size=20, color="amber")
        draw_text(surface, self.data["rounds"][self.round]["q"], 60, 185,
                  size=22, color="white", max_width=WIDTH - 120)
        for btn in self.option_btns:
            btn.draw(surface)
        if self.feedback:
            draw_text(surface, self.feedback, 60, 250 + 4 * 64, size=20,
                      color="green" if "Correct" in self.feedback else "red")


class FlagBoss(Scene):
    """Threat hunt: flag the bad items, then run a scan to check your work.

    data = {
        "prompt":     "instruction line",
        "items":      [ {"label": "...", "detail": "...", "bad": True/False,
                         "reason": "shown after the scan"}, ... ],
        "scan_label": "Run Scan",
        "win":        "message when every item is judged correctly",
    }
    """

    def __init__(self, game, data, title):
        super().__init__(game)
        self.data = data
        self.title = title
        # Give each item its own "flagged" state without touching the original data.
        self.items = [dict(it, flagged=False) for it in data["items"]]
        self.row_rects = []
        self.scanned = False
        self.won = False
        self.message = data.get("prompt", "Flag the dangerous items, then scan.")
        self.scan_btn = Button(60, HEIGHT - 84, 240, 52,
                               data.get("scan_label", "Run Scan"), color="amber")
        self.continue_btn = Button(WIDTH - 240, HEIGHT - 84, 200, 52, "Continue >")

    def evaluate(self):
        self.scanned = True
        wrong = sum(1 for it in self.items if it["flagged"] != it["bad"])
        if wrong == 0:
            self.won = True
            self.message = self.data.get("win", "All threats correctly identified!")
        else:
            self.message = f"{wrong} wrong. Read the notes and adjust your flags."

    def handle_event(self, event):
        if self.won:
            if self.continue_btn.handle_event(event):
                self.next_scene = self.return_to
            return
        if self.scan_btn.handle_event(event):
            self.evaluate()
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for i, rect in enumerate(self.row_rects):
                if rect.collidepoint(event.pos):
                    self.items[i]["flagged"] = not self.items[i]["flagged"]

    def draw(self, surface):
        surface.fill(COLORS["bg"])
        self.draw_header(surface, self.title)
        draw_text(surface, self.message, 60, 88, size=19,
                  color="green" if self.won else "amber", max_width=WIDTH - 120)

        self.row_rects = []
        # Size rows to fit however many items there are.
        n = len(self.items)
        row_h = max(44, min(64, (HEIGHT - 230) // max(1, n)))
        y = 128
        for i, it in enumerate(self.items):
            rect = pygame.Rect(60, y, WIDTH - 120, row_h - 8)
            self.row_rects.append(rect)
            if self.scanned and it["bad"]:
                bg = COLORS["red"] if it["flagged"] else COLORS["panel2"]
            elif it["flagged"]:
                bg = (70, 30, 30)
            else:
                bg = COLORS["panel"]
            pygame.draw.rect(surface, bg, rect, border_radius=8)
            pygame.draw.rect(surface, COLORS["gray"], rect, width=1, border_radius=8)
            mark = "[FLAG]" if it["flagged"] else "[    ]"
            draw_text(surface, mark, 74, y + 6, size=16,
                      color="red" if it["flagged"] else "gray")
            draw_text(surface, it["label"], 168, y + 6, size=19, color="white")
            if self.scanned:
                verdict = "THREAT" if it["bad"] else "SAFE"
                vcolor = "red" if it["bad"] else "green"
                draw_text(surface, f"{verdict}: {it.get('reason', '')}", 168,
                          y + 28, size=13, color=vcolor, max_width=WIDTH - 280)
            elif it.get("detail"):
                draw_text(surface, it["detail"], 168, y + 28, size=13,
                          color="gray", max_width=WIDTH - 280)
            y += row_h

        if self.won:
            self.continue_btn.draw(surface)
        else:
            self.scan_btn.draw(surface)
