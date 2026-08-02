"""
make_icon.py  --  generates assets/icon.ico (a neon shield) for the game.

Run once with:  python make_icon.py
It draws the icon with pygame, saves a PNG, then wraps that PNG into a Windows
.ico file by hand (no extra libraries needed). Safe to delete after running.
"""
import os, struct
os.environ["SDL_VIDEODRIVER"] = "dummy"      # render without opening a window
import pygame

pygame.init()
SIZE = 256
surf = pygame.Surface((SIZE, SIZE), pygame.SRCALPHA)   # SRCALPHA = transparency

BG     = (14, 16, 24)
GREEN  = (57, 255, 137)
DGREEN = (20, 90, 55)
DARK   = (10, 12, 18)

# Rounded dark tile background.
pygame.draw.rect(surf, BG, (0, 0, SIZE, SIZE), border_radius=48)

# A shield shape (a polygon: list of (x, y) corner points).
shield = [
    (128, 28), (210, 60), (210, 140),
    (128, 228), (46, 140), (46, 60),
]
pygame.draw.polygon(surf, DGREEN, shield)              # filled body
pygame.draw.polygon(surf, GREEN, shield, width=8)      # bright outline

# A keyhole in the centre (a circle plus a tapered slot) = "security".
pygame.draw.circle(surf, DARK, (128, 120), 26)
pygame.draw.polygon(surf, DARK, [(116, 130), (140, 130), (134, 178), (122, 178)])

# A little "7" nod to your codename CIPHER-7, top-right.
f = pygame.font.SysFont("consolas", 40, bold=True)
img = f.render("7", True, GREEN)
surf.blit(img, (182, 30))

os.makedirs("assets", exist_ok=True)
png_path = "assets/icon.png"
pygame.image.save(surf, png_path)                      # pygame writes PNG natively
pygame.quit()

# --- wrap the PNG bytes into a minimal .ico container (Vista+ supports PNG) ---
with open(png_path, "rb") as fh:
    png = fh.read()

# ICONDIR header (6 bytes) + one ICONDIRENTRY (16 bytes), then the PNG data.
header = struct.pack("<HHH", 0, 1, 1)                  # reserved, type=icon, count=1
entry = struct.pack("<BBBBHHII",
                    0, 0,        # width, height (0 = 256)
                    0, 0,        # palette count, reserved
                    1, 32,       # color planes, bits-per-pixel
                    len(png),    # size of the image data
                    6 + 16)      # offset to the image data
with open("assets/icon.ico", "wb") as fh:
    fh.write(header + entry + png)

print("Wrote assets/icon.ico  (", len(png), "bytes of PNG inside )")
