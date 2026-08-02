"""
effects.py  --  small visual animations to make the game feel alive.
====================================================================

MatrixRain -- the classic "falling green code" backdrop. It's drawn BEHIND the
              normal screen content, dimmed, so it adds atmosphere without
              hurting readability.

The trick is cheap and beginner-friendly: the screen is divided into vertical
columns. Each column has a "head" that falls downward; we draw a bright
character at the head and a few dimmer ones trailing above it.
"""
import random
import pygame
from engine import font, COLORS

# The pool of characters that can appear in the rain.
CHARS = "01<>[]{}#$%&*+=ABCDEF0123456789"


class MatrixRain:
    def __init__(self, width, height, spacing=20, speed=140):
        self.width = width
        self.height = height
        self.spacing = spacing                       # pixels between columns
        self.columns = width // spacing
        self.font = font(18)
        # Each column gets a starting height and a slightly random fall speed.
        self.y = [random.uniform(-height, 0) for _ in range(self.columns)]
        self.speed = [random.uniform(speed * 0.5, speed * 1.5)
                      for _ in range(self.columns)]
        # A character for each column that occasionally changes.
        self.heads = [random.choice(CHARS) for _ in range(self.columns)]
        self.flicker = 0.0

    def update(self, dt):
        self.flicker += dt
        change = self.flicker > 0.08                  # swap some characters now?
        if change:
            self.flicker = 0.0
        for i in range(self.columns):
            self.y[i] += self.speed[i] * dt           # fall downward
            if self.y[i] > self.height + 40:          # off the bottom? restart on top
                self.y[i] = random.uniform(-200, -20)
                self.speed[i] = random.uniform(70, 210)
            if change and random.random() < 0.15:
                self.heads[i] = random.choice(CHARS)

    def draw(self, surface):
        trail = 6                                     # how many dim characters trail
        for i in range(self.columns):
            x = i * self.spacing
            head_y = self.y[i]
            # The bright leading character.
            img = self.font.render(self.heads[i], True, COLORS["green"])
            surface.blit(img, (x, head_y))
            # Dimmer characters fading upward behind it.
            for t in range(1, trail):
                ty = head_y - t * self.spacing
                if ty < -20:
                    continue
                fade = int(180 * (1 - t / trail))     # gets darker the higher it is
                color = (0, fade, int(fade * 0.5))
                ch = CHARS[(i + t) % len(CHARS)]
                img = self.font.render(ch, True, color)
                surface.blit(img, (x, ty))
