"""
main.py  --  Run this file to play:   python main.py
============================================================

This is the "conductor". It does three jobs:
    1) opens the game window,
    2) runs the GAME LOOP (the heartbeat that repeats ~60x per second),
    3) keeps track of WHICH scene is on screen and switches between them.

The actual content lives elsewhere:
    - engine.py      -> the toolkit (buttons, text, the Scene base class)
    - story.py       -> all the words
    - levels/        -> one file per level

Read engine.py first, then this file, then the levels in order. Enjoy.
"""

import os
import sys
import math
import pygame

import engine
from engine import Scene, Button, draw_text, COLORS, WIDTH, HEIGHT
import story
import save                                   # remembers progress between sessions
import audio                                  # sound effects + music
import lessons                                # the beginner Python lesson cards
import bootcamp                               # Level 0: the absolute-beginner intro
import handoff                                # lets the 3D office request a level
import datalevels                             # extra levels defined purely as data
from bosses import QuizBoss, FlagBoss         # the reusable data-driven boss fights
from effects import MatrixRain                # the falling-code background

# The two new learning scenes (the hacker explainer and the Python terminal lab).
from labscene import IntelScene, LabScene
# Bonus screens reachable from the menu.
from extras import SandboxScene, GlossaryScene, LevelSelectScene

# Import each level MODULE. Each module provides three things we use:
#   - a boss Scene class (Level1 ... Level9)
#   - INTEL      : the "what the hacker does" sections
#   - CHALLENGES : the hands-on Python terminal tasks
from levels import (level1_passwords, level2_cipher, level3_phishing,
                    level4_network, level5_injection, level6_malware,
                    level7_hashing, level8_twofactor, level9_null)

# Map each level number to its module, plus a short topic name for the lab header.
LEVEL_MODULES = {1: level1_passwords, 2: level2_cipher, 3: level3_phishing,
                 4: level4_network, 5: level5_injection, 6: level6_malware,
                 7: level7_hashing, 8: level8_twofactor, 9: level9_null}
LAB_TOPICS = {1: "Variables, Strings & Loops",
              2: "Functions, ord/chr & Modulo",
              3: "Lists & Dictionaries",
              4: "Dictionaries & Lookups",
              5: "Strings & f-strings",
              6: "Classes & Objects",
              7: "Hashing & the hashlib library",
              8: "Modulo, Strings & Functions",
              9: "Capstone -- Everything"}


# ---------------------------------------------------------------------------
# THE CAMPAIGN  --  one ordered list of levels, in play order.
# ---------------------------------------------------------------------------
# Each level is described by a "provider": a dict of its content plus a
# `make_boss(game, return_to, title)` function that builds its boss. We mix two
# sources: the hand-built modules (rich, bespoke bosses) and the data-only levels
# from datalevels.py (which use the reusable QuizBoss / FlagBoss). NULL always
# sits last. To add levels later, just append to datalevels.DATA_LEVELS -- the
# numbering, menu, save system and level-select all follow automatically.

def _attach(scene, return_to):
    """Tell a freshly-built boss where to go when it's beaten, then return it."""
    scene.return_to = return_to
    return scene

def _legacy_provider(n):
    """Wrap one of the hand-built level modules as a provider."""
    mod = LEVEL_MODULES[n]
    boss_cls = getattr(mod, f"Level{n}")       # e.g. Level1, Level9
    boss_name, brief = story.BRIEFINGS[n]
    return {
        "boss": boss_name,
        "topic": LAB_TOPICS[n],
        "brief": brief,
        "debrief": story.DEBRIEFS[n],
        "intel": mod.INTEL,
        "lesson": lessons.LESSONS[n],
        "challenges": mod.CHALLENGES,
        "make_boss": (lambda g, rt, title, c=boss_cls: _attach(c(g), rt)),
    }

def _data_provider(d):
    """Wrap a data-only level (from datalevels.py) as a provider."""
    boss_cls = QuizBoss if d["boss_kind"] == "quiz" else FlagBoss
    return {
        "boss": d["boss"],
        "topic": d["topic"],
        "brief": d["brief"],
        "debrief": d["debrief"],
        "intel": d["intel"],
        "lesson": d["lesson"],
        "challenges": d["challenges"],
        "make_boss": (lambda g, rt, title, c=boss_cls, data=d["boss_data"]:
                      _attach(c(g, data, title), rt)),
    }

# Order: the original six lieutenants, the new data-driven training levels, then
# RIPPER and RELAY, and finally NULL. (Numbers are assigned by position below.)
CAMPAIGN = (
    [_legacy_provider(n) for n in (1, 2, 3, 4, 5, 6)]      # Cracker .. Plague
    + [_data_provider(d) for d in datalevels.DATA_LEVELS]  # BRUTUS, VEX, SCRIPTER...
    + [_legacy_provider(7), _legacy_provider(8)]           # RIPPER, RELAY
    + [_legacy_provider(9)]                                # NULL -- always last
)

# The total number of story levels, derived from the campaign so we never have
# to hand-update a magic number when adding levels.
NUM_LEVELS = len(CAMPAIGN)


# ---------------------------------------------------------------------------
# SIMPLE STORY SCREENS (title, briefings, debriefs, outro)
# ---------------------------------------------------------------------------
class TitleScene(Scene):
    """The opening menu. Its buttons change depending on your saved progress."""

    def __init__(self, game):
        super().__init__(game)
        # Background animation + a dim sheet so text stays readable over it.
        self.rain = MatrixRain(WIDTH, HEIGHT)
        self.dim = pygame.Surface((WIDTH, HEIGHT))
        self.dim.fill(COLORS["bg"])
        self.dim.set_alpha(150)             # 0 = invisible, 255 = solid
        self.t = 0.0                        # a timer used to pulse the title
        # We build a list of (Button, action) pairs so the click handler is simple.
        self.buttons = []
        completed = game.progress["completed"]
        x, w, h = WIDTH // 2 - 160, 320, 42
        y, gap = 288, 48

        def add(label, action, color="green"):
            nonlocal y
            self.buttons.append((Button(x, y, w, h, label, color=color), action))
            y += gap

        # Offer "Continue" only when there's an unfinished mission to resume.
        if 0 < completed < NUM_LEVELS:
            add(f"Continue  (Level {completed + 1})", "continue")
            add("New Game", "newgame", color="gray")
            add("Boot Camp", "bootcamp", color="cyan")
            add("Field Notes  (lists & loops)", "fieldnotes", color="cyan")
        elif completed >= NUM_LEVELS:
            add("Play Again", "newgame")
            add("Boot Camp", "bootcamp", color="cyan")
            add("Field Notes  (lists & loops)", "fieldnotes", color="cyan")
        else:
            # Brand-new player: put Boot Camp first as the gentle starting point.
            add("Boot Camp  (new? start here)", "bootcamp")
            add("Start Mission", "newgame", color="cyan")
            # The second on-ramp, for anyone who found Level 1 steep. Offered
            # rather than imposed -- nothing is gated behind it.
            add("Field Notes  (lists & loops)", "fieldnotes", color="cyan")
        add("Select Level  (replay)", "levels", color="cyan")
        add("Free Play  (Sandbox)", "sandbox", color="cyan")
        add("Glossary", "glossary", color="cyan")
        add("Quit", "quit", color="gray")

    def do(self, action):
        completed = self.game.progress["completed"]
        if action == "continue":
            self.next_scene = f"brief{completed + 1}"
        elif action == "newgame":
            # Forget old progress and the carried-over lab toolkit, then start over.
            self.game.toolkit.clear()
            self.game.progress = save.reset()
            self.next_scene = "intro"
        elif action == "bootcamp":
            self.next_scene = "bootcamp0"
        elif action == "fieldnotes":
            self.next_scene = "bootcamp29"
        elif action == "levels":
            self.next_scene = "levels"
        elif action == "sandbox":
            self.next_scene = "sandbox"
        elif action == "glossary":
            self.next_scene = "glossary"
        elif action == "quit":
            self.game.running = False

    def handle_event(self, event):
        for btn, action in self.buttons:
            if btn.handle_event(event):
                self.do(action)

    def update(self, dt):
        self.rain.update(dt)                # animate the falling code
        self.t += dt                        # advance the title-pulse timer

    def draw(self, surface):
        surface.fill(COLORS["bg"])
        self.rain.draw(surface)             # falling code behind everything
        surface.blit(self.dim, (0, 0))      # dim it so the menu reads clearly

        # Pulse the title's brightness with a slow sine wave (0.6 .. 1.0).
        pulse = 0.6 + 0.4 * (0.5 + 0.5 * math.sin(self.t * 2.0))
        g = COLORS["green"]
        title_color = (int(g[0] * pulse), int(g[1] * pulse), int(g[2] * pulse))
        draw_text(surface, "NULL  COLLECTIVE", WIDTH // 2, 92, size=60,
                  color=title_color, center=True)
        draw_text(surface, "an ethical-hacking adventure", WIDTH // 2, 164,
                  size=23, color="cyan", center=True)
        draw_text(surface, f"You are {story.HERO} -- the vigilante who fights "
                  "hackers with their own tools.", WIDTH // 2, 214, size=18,
                  color="gray", center=True, max_width=720)

        completed = self.game.progress["completed"]
        if completed > 0:
            draw_text(surface, f"Progress: {completed} / {NUM_LEVELS} levels cleared",
                      WIDTH // 2, 250, size=17, color="amber", center=True)

        for btn, _ in self.buttons:
            btn.draw(surface)
        draw_text(surface, "ESC: menu     M: mute sound",
                  WIDTH // 2, HEIGHT - 34, size=15, color="gray", center=True)


class TextScene(Scene):
    """A reusable 'read some story, then click Continue' screen.

    We use ONE class for the intro, every briefing, every debrief, and the outro
    by just feeding it different text and a different next-scene target. That's
    the power of writing flexible code once instead of seven near-copies.
    """

    def __init__(self, game, title, body, button_label, target,
                 title_color="green"):
        super().__init__(game)
        self.title = title
        self.body = body
        self.target = target               # the scene name to go to on Continue
        self.title_color = title_color
        self.btn = Button(WIDTH - 260, HEIGHT - 90, 220, 56, button_label)
        # A faint falling-code backdrop. Dimmed heavily so the story stays easy
        # to read over it.
        self.rain = MatrixRain(WIDTH, HEIGHT)
        self.dim = pygame.Surface((WIDTH, HEIGHT))
        self.dim.fill(COLORS["bg"])
        self.dim.set_alpha(205)

    def handle_event(self, event):
        if self.btn.handle_event(event):
            self.next_scene = self.target

    def update(self, dt):
        self.rain.update(dt)

    def draw(self, surface):
        surface.fill(COLORS["bg"])
        self.rain.draw(surface)
        surface.blit(self.dim, (0, 0))
        draw_text(surface, self.title, 60, 70, size=40, color=self.title_color)
        pygame.draw.line(surface, COLORS["green"], (60, 130), (WIDTH - 60, 130), 1)
        draw_text(surface, self.body, 60, 160, size=22, color="white",
                  max_width=WIDTH - 120, line_gap=8)
        self.btn.draw(surface)


# ---------------------------------------------------------------------------
# THE GAME OBJECT  (owns the window, the loop, and the scene switching)
# ---------------------------------------------------------------------------
class Game:
    def __init__(self):
        pygame.init()                                  # wake up pygame
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("NULL Collective")
        # Use our shield as the window/taskbar icon. Wrapped in try/except so the
        # game still runs even if the icon file is ever missing.
        try:
            # Build an ABSOLUTE path from this file's own folder. A plain
            # "assets/icon.png" is relative to whatever folder the game was
            # STARTED from -- fine when you double-click it, but the 3D office
            # launches us from somewhere else and the icon would silently vanish.
            here = os.path.dirname(os.path.abspath(__file__))
            icon = pygame.image.load(os.path.join(here, "assets", "icon.png"))
            pygame.display.set_icon(icon)
        except Exception:
            pass
        audio.init()                                   # start sound + music

        # For the fade-in transition: a black sheet we lay over a new scene and
        # fade away. `fade_alpha` 255 = fully black, 0 = gone.
        self._fade_surf = pygame.Surface((WIDTH, HEIGHT))
        self._fade_surf.fill((0, 0, 0))
        self.fade_alpha = 0
        # A small always-on mute toggle in the top-right corner. Clicking it works
        # on EVERY screen -- including the labs, where the keyboard is busy being
        # typed into, so a keyboard mute shortcut there would steal your letters.
        self.mute_btn = Button(WIDTH - 130, 16, 114, 36, "SOUND: ON", color="gray")
        self.clock = pygame.time.Clock()               # used to cap the frame rate
        self.running = True
        self.progress = save.load()                    # {"completed": N} from disk
        # How many levels there are, and each boss's name -- handy for the menu
        # and the level-select screen (which can't import this module directly).
        self.num_levels = NUM_LEVELS
        self.level_names = [prov["boss"] for prov in CAMPAIGN]
        # The "toolkit": functions YOU define in the labs get collected here and
        # carried into the boss fights, so the boss can run the code you wrote.
        self.toolkit = {}

        # --- The 3D office handoff (see handoff.py) -------------------------
        # If the office launched us with "--level 3", this is a dict; if you
        # started the game normally it is None and everything below behaves
        # exactly as it always has.
        self.request = handoff.read_request()
        self.last_level_n = None        # which level's debrief we reached
        self.run_stats = None           # the lab's tally, filled in by LabScene
        # Latched the moment the REQUESTED level is finished, so wandering off
        # afterwards (ESC to the menu, replaying something else) can't change
        # the verdict the office receives.
        self.handoff_cleared = False
        self.handoff_stats = None

        # `factories` maps a scene NAME to a function that builds a FRESH copy of
        # that scene. Building fresh each time means levels reset properly when
        # you replay them. We pass `self` (the game) into every scene.
        self.factories = self._build_factories()

        # Normally we open on the title menu. If the office asked for a specific
        # level, jump straight into that level's briefing instead.
        start = "menu"
        if self.request:
            # Level 0 is the Boot Camp, which has no briefing and no boss --
            # it's a lesson and a tiny lab, so it starts somewhere different.
            # A boot camp has no briefing screen, so it starts somewhere else.
            wanted = (f"bootcamp{self.request['level']}"
                      if self.request["level"] in bootcamp.EXTRA_MODULES
                      else f"brief{self.request['level']}")
            if wanted in self.factories:
                start = wanted
        self.scene = self.factories[start]()

    def _build_factories(self):
        g = self
        factories = {
            "menu":  lambda: TitleScene(g),
            "intro": lambda: TextScene(g, "THE CALL", story.INTRO,
                                       "Begin >", "brief1"),
            "outro": lambda: TextScene(g, "VICTORY", story.OUTRO,
                                       "Main Menu >", "menu", title_color="cyan"),
            "sandbox": lambda: SandboxScene(g),
            "glossary": lambda: GlossaryScene(g),
            "levels": lambda: LevelSelectScene(g),
            # (the boot camps are added just below, from bootcamp.EXTRA_MODULES)
            # Shown ONLY when the 3D office asked for this level. Its button
            # closes the game so the office gets control back. Without this the
            # debrief would chain into the NEXT level's briefing and the office
            # would wait forever.
            "handoff_done": lambda: TextScene(
                g, "TASK COMPLETE",
                "Corrective action recorded.\n\n"
                "Close this window to return to the office and file your ticket.",
                "Return to the office >", "__quit__", title_color="cyan"),
        }
        # --- the boot camps ----------------------------------------------
        # Optional on-ramps, not campaign missions: a lesson and a small lab,
        # no villain and no boss. They're built from one table so adding
        # another needs no new code here.
        #
        # Each gets scenes named after its level number, e.g. "bootcamp0" and
        # "bootcamp0lab". When the office asked for one, the lab hands control
        # back instead of returning to our menu -- a boot camp has no debrief,
        # so finishing its lab IS finishing the mission.
        for bc_level, mod in bootcamp.EXTRA_MODULES.items():
            asked = bool(self.request and self.request["level"] == bc_level)
            factories[f"bootcamp{bc_level}"] = (
                lambda n=bc_level, mod=mod:
                IntelScene(g, n, mod["title"] + ": CODING FROM ZERO"
                           if n == 0 else mod["title"],
                           mod["lesson"], f"bootcamp{n}lab",
                           code_label="// example:", accent="cyan",
                           final_label="Open the Lab >")
            )
            factories[f"bootcamp{bc_level}lab"] = (
                lambda n=bc_level, mod=mod, asked=asked:
                LabScene(g, n, mod["title"], mod["challenges"],
                         "handoff_done" if asked else "menu",
                         final_label=("Done -- back to the office >" if asked
                                      else "Done -- Back to Menu >"))
            )

        # Every level is a 5-part mission, built from its campaign provider:
        #   brief{n} -> intel{n} -> lesson{n} -> lab{n} -> level{n} (boss) -> debrief{n}
        for i, prov in enumerate(CAMPAIGN, start=1):
            after_debrief = f"brief{i + 1}" if i < NUM_LEVELS else "outro"
            # If the office asked for THIS level, its debrief must end the
            # session instead of rolling on into the next mission.
            if self.request and self.request["level"] == i:
                after_debrief = "handoff_done"
            title = f"LEVEL {i}  //  {prov['boss']}"

            # Default arguments (i=i, prov=prov, ...) "freeze" the current values so
            # each lambda remembers ITS OWN level, not the last one in the loop.
            factories[f"brief{i}"] = (
                lambda i=i, prov=prov:
                TextScene(g, f"LEVEL {i}:  {prov['boss']}", prov["brief"],
                          "Intel >", f"intel{i}")
            )
            # Intel: what the hacker does (red 'attacker' styling) -> the Lesson.
            factories[f"intel{i}"] = (
                lambda i=i, prov=prov:
                IntelScene(g, i, f"INTEL: {prov['boss']}", prov["intel"],
                           f"lesson{i}", code_label="// what the attacker runs:",
                           accent="red", final_label="Python Lesson >")
            )
            # Lesson: the Python, taught slowly (green 'example' styling) -> the Lab.
            factories[f"lesson{i}"] = (
                lambda i=i, prov=prov:
                IntelScene(g, i, "PYTHON LESSON", prov["lesson"], f"lab{i}",
                           code_label="// try this example:", accent="green",
                           final_label="Enter the Lab >")
            )
            factories[f"lab{i}"] = (
                lambda i=i, prov=prov:
                LabScene(g, i, prov["topic"], prov["challenges"], f"level{i}")
            )
            factories[f"level{i}"] = (
                lambda i=i, prov=prov, title=title:
                prov["make_boss"](g, f"debrief{i}", title)
            )
            factories[f"debrief{i}"] = (
                lambda i=i, prov=prov, after=after_debrief:
                TextScene(g, "MISSION DEBRIEF", prov["debrief"], "Continue >",
                          after, title_color="amber")
            )
        return factories

    def mark_complete_if_debrief(self, name):
        """If we're entering a debrief screen, that level is finished -- record it."""
        # Boot Camp is the exception: it has no boss and no debrief, so reaching
        # the end of its lab IS finishing it. Without this the office would wait
        # for a debrief that never comes and grade a completed Boot Camp as
        # "you left early".
        if name == "handoff_done" and self.request \
                and self.request["level"] in bootcamp.EXTRA_MODULES:
            self.last_level_n = self.request["level"]
            self.handoff_cleared = True
            self.handoff_stats = dict(self.run_stats) if self.run_stats else {}
            audio.play("win")
            return

        if name.startswith("debrief"):
            try:
                n = int(name[len("debrief"):])         # "debrief3" -> 3
            except ValueError:
                return
            self.last_level_n = n                      # remember for the report

            # Did we just finish the mission the office sent us to do? Latch it
            # NOW, together with the lab tally, so nothing done afterwards can
            # rewrite history.
            if self.request and n == self.request["level"]:
                self.handoff_cleared = True
                self.handoff_stats = dict(self.run_stats) if self.run_stats else {}

            # Only the standalone campaign advances savegame.json. An office
            # mission can send you to level 9 on your first day; recording that
            # here would mark levels 1-8 complete in the standalone game and let
            # you skip content you never played. The office keeps its own record
            # in intern.json, so nothing is lost.
            if self.request is None and n > self.progress["completed"]:
                self.progress["completed"] = n
                save.save(self.progress)               # persist to savegame.json

            audio.play("win")                          # celebrate a beaten level

    def go_to(self, name):
        """Switch to a brand-new instance of the named scene."""
        # "__quit__" isn't a real screen -- it's how the handoff end screen tells
        # us to shut down so the 3D office can take over again.
        if name == "__quit__":
            self.running = False
            return
        self.mark_complete_if_debrief(name)
        if name in self.factories:
            self.scene = self.factories[name]()
            self.fade_alpha = 255                      # start the new scene fully
            #                                            black, then fade it in
        else:
            print("WARNING: unknown scene", name)      # a helpful safety net

    def run(self):
        """The GAME LOOP. Each pass = one frame: events -> update -> draw."""
        while self.running:
            # dt = seconds since the previous frame; tick(FPS) also caps the speed.
            dt = self.clock.tick(engine.FPS) / 1000.0

            # 1) EVENTS: react to the keyboard, mouse, and window close button.
            for event in pygame.event.get():
                if event.type == pygame.QUIT:          # clicked the window's X
                    self.running = False
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    self.go_to("menu")                 # bail back to the menu
                elif (event.type == pygame.KEYDOWN and event.key == pygame.K_m
                        and not getattr(self.scene, "captures_text", False)):
                    # M = mute, but ONLY on screens that aren't capturing typing.
                    # In a lab/sandbox you need to type the letter 'm', so there
                    # you mute with the on-screen button instead.
                    audio.toggle_mute()
                elif self.mute_btn.handle_event(event):
                    audio.toggle_mute()                # the clickable mute toggle
                else:
                    self.scene.handle_event(event)     # let the scene handle it

            # 2) UPDATE: advance animations / check win conditions.
            self.scene.update(dt)

            # 3) If the scene asked to move on, switch now.
            if self.scene.next_scene is not None:
                self.go_to(self.scene.next_scene)

            # 4) DRAW: paint this frame.
            self.scene.draw(self.screen)

            # 5) Fade the scene in from black (the overlay shrinks each frame).
            if self.fade_alpha > 0:
                self.fade_alpha = max(0, self.fade_alpha - 600 * dt)
                self._fade_surf.set_alpha(int(self.fade_alpha))
                self.screen.blit(self._fade_surf, (0, 0))

            # 6) Draw the mute button LAST so it's always visible and never dimmed.
            self.mute_btn.label = "MUTED" if audio.muted else "SOUND: ON"
            self.mute_btn.draw(self.screen)

            pygame.display.flip()                      # reveal the finished frame

        # The loop has ended, whatever the reason -- finished the mission, hit
        # ESC, or closed the window. Report back BEFORE we shut down, so every
        # exit route tells the office something rather than leaving it guessing.
        self.write_handoff_report()

        pygame.quit()                                  # clean shutdown
        sys.exit()

    def write_handoff_report(self):
        """Tell the 3D office what happened this session (see handoff.py)."""
        if not self.request:
            return                                     # nobody is listening

        asked = self.request["level"]
        # Use the tally we snapshotted when the asked level was cleared. Fall
        # back to whatever the last lab produced ONLY if it is stamped with the
        # level we were asked about -- otherwise report no lab data at all,
        # which grades as "not clean" rather than as somebody else's score.
        stats = self.handoff_stats
        if stats is None:
            stats = self.run_stats or {}
        if stats.get("level") != asked:
            stats = {}

        report = {
            "session_id":   self.request["session"],
            "asked_level":  asked,
            "finished_level": self.last_level_n,
            # Latched when the asked level's debrief was reached (see above).
            "cleared":      self.handoff_cleared,
            # The lab tally. Empty if the player never reached the lab.
            "challenges":   stats.get("challenges", 0),
            "solved":       stats.get("solved", 0),
            "hints_shown":  stats.get("hints", 0),
            "solutions_shown": stats.get("solutions", 0),
            "skips":        stats.get("skips", 0),
        }
        # Work out the grade HERE, in one place, so the office never has to
        # re-derive it and the two games can never disagree about what "clean"
        # means. See handoff.is_clean() for the rule (hints are free).
        report["clean"] = handoff.is_clean(report)
        handoff.write_report(self.request["report"], report)


# This standard line means "only run the game if THIS file was launched directly"
# (not if it was imported by another file). It's a common Python pattern.
if __name__ == "__main__":
    Game().run()
