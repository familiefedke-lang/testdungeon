"""
main.py – bootstrap pygame and start the game.

Usage:
    python -m src.main
or:
    python src/main.py   (from repo root)
"""

from __future__ import annotations

import os
import sys

# Ensure repo root is on sys.path so `src.*` imports work when run directly.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pygame

from src.constants import WINDOW_W, WINDOW_H, TITLE, TILE
from src.engine import Engine
from src.game import Game
from src.render.renderer import Renderer
from src.render.spritesheet import Spritesheet
from src.render.animations import AnimationDB
from src.render.items_atlas import ItemsAtlas


# ---------------------------------------------------------------------------
# Asset paths (relative to repo root)
# ---------------------------------------------------------------------------

_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

ATLAS_PNG = os.path.join(_REPO_ROOT, "assets", "sprites", "atlas.png")
ATLAS_JSON = os.path.join(_REPO_ROOT, "assets", "sprites", "atlas.json")

ITEMS_PNG = os.path.join(_REPO_ROOT, "assets", "sprites", "items.png")
ITEMS_ATLAS_JSON = os.path.join(_REPO_ROOT, "assets", "sprites", "items.atlas.json")


def main() -> None:
    pygame.init()
    pygame.display.set_caption(TITLE)

    screen = pygame.display.set_mode((WINDOW_W, WINDOW_H))

    # Generate atlas if it doesn't exist yet
    if not os.path.exists(ATLAS_PNG):
        _generate_placeholder_atlas(ATLAS_PNG)

    # Load animation db first so tilesPerRow is respected
    animation_db = AnimationDB(ATLAS_JSON)
    spritesheet = Spritesheet(
        ATLAS_PNG,
        tile_size=TILE,
        tiles_per_row=animation_db.tiles_per_row,
    )

    # Items sheet
    items_atlas = ItemsAtlas(ITEMS_ATLAS_JSON)
    items_spritesheet = Spritesheet(
        ITEMS_PNG,
        tile_size=TILE,
        tiles_per_row=items_atlas.tiles_per_row,
    )

    font = pygame.font.SysFont("monospace", 14)

    renderer = Renderer(screen, spritesheet, animation_db, items_spritesheet, items_atlas, font)
    engine = Engine(animation_db)

    game = Game(engine, renderer)
    game.run()

    pygame.quit()


def _generate_placeholder_atlas(path: str) -> None:
    """
    Generate a minimal placeholder atlas.png at *path*.

    Layout (8 tiles per row, 32×32 each):
      Index 0 → WALL  (dark grey)
      Index 1 → FLOOR (mid-grey)
      Index 2 → STAIRS (yellow-green)
      Index 3 → player idle S frame 0 (blue silhouette)
      Index 4 → player walk S frame 0 (brighter blue)
      Index 5 → player attack S frame 0 (cyan)
      Index 6 → player hurt S (orange)
      Index 7 → player dead S (dark red)
      Index 8 → goblin idle S (green)
      Index 9 → goblin walk S (bright green)
      Index 10 → goblin attack S (yellow)
      Index 11 → goblin hurt (orange-red)
      Index 12 → goblin dead (brown)
    """
    import pygame

    pygame.init()
    TILES_PER_ROW = 8
    T = 32
    total_tiles = 16  # we define 13, pad to 16
    rows = (total_tiles + TILES_PER_ROW - 1) // TILES_PER_ROW
    width = TILES_PER_ROW * T
    height = rows * T

    atlas = pygame.Surface((width, height), pygame.SRCALPHA)
    atlas.fill((0, 0, 0, 0))

    palette = [
        (50,  50,  60),   # 0 WALL
        (90,  80,  70),   # 1 FLOOR
        (180, 200, 60),   # 2 STAIRS
        (60,  100, 200),  # 3 player idle
        (80,  130, 220),  # 4 player walk
        (100, 210, 230),  # 5 player attack
        (230, 140,  40),  # 6 player hurt
        (120,  30,  30),  # 7 player dead
        (50,  140,  50),  # 8 goblin idle
        (70,  180,  70),  # 9 goblin walk
        (200, 200,  40),  # 10 goblin attack
        (220, 100,  40),  # 11 goblin hurt
        (110,  70,  30),  # 12 goblin dead
        (30,   30,  30),  # 13 (spare)
        (30,   30,  30),  # 14 (spare)
        (30,   30,  30),  # 15 (spare)
    ]

    for idx, color in enumerate(palette):
        col = idx % TILES_PER_ROW
        row = idx // TILES_PER_ROW
        rect = pygame.Rect(col * T, row * T, T, T)
        pygame.draw.rect(atlas, color, rect)
        cx, cy = rect.centerx, rect.centery
        pygame.draw.circle(atlas, (255, 255, 255, 80), (cx, cy), T // 4 - 2)

    os.makedirs(os.path.dirname(path), exist_ok=True)
    pygame.image.save(atlas, path)


if __name__ == "__main__":
    main()