"""
Renderer – thin drawing API around pygame.

All *x, y* positional arguments use **tile coordinates** unless the
method name says "px" (pixel coordinates).
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pygame

from src.constants import TILE
from src.world.tiles import TILE_SPRITE

if TYPE_CHECKING:
    from src.ecs.entity import Actor
    from src.render.spritesheet import Spritesheet
    from src.render.animations import AnimationDB


class Renderer:
    BG_COLOR = (10, 10, 20)
    UI_COLOR = (220, 220, 220)
    HP_BAR_FG = (180, 30, 30)
    HP_BAR_BG = (60, 60, 60)

    def __init__(
        self,
        screen: pygame.Surface,
        spritesheet: "Spritesheet",
        animation_db: "AnimationDB",
        font: pygame.font.Font,
    ) -> None:
        self.screen = screen
        self.spritesheet = spritesheet
        self.animation_db = animation_db
        self.font = font

    # ------------------------------------------------------------------
    # Frame helpers
    # ------------------------------------------------------------------

    def clear(self) -> None:
        self.screen.fill(self.BG_COLOR)

    def present(self) -> None:
        pygame.display.flip()

    # ------------------------------------------------------------------
    # Tile drawing
    # ------------------------------------------------------------------

    def draw_tile(self, tile_type, x: int, y: int) -> None:
        """Draw a map tile at tile coordinates (x, y)."""
        fallback = TILE_SPRITE.get(tile_type, 0)
        tile_index = self.animation_db.get_tile_sprite(tile_type.name.lower(), fallback)
        surface = self.spritesheet.get_tile_surface(tile_index)
        self.screen.blit(surface, (x * TILE, y * TILE))

    # ------------------------------------------------------------------
    # Actor drawing
    # ------------------------------------------------------------------

    def draw_actor(self, actor: "Actor") -> None:
        if actor.sprite is None:
            return
        frame_index = actor.sprite.current_frame_index(self.animation_db)
        surface = self.spritesheet.get_tile_surface(frame_index)
        self.screen.blit(surface, (actor.x * TILE, actor.y * TILE))

    # ------------------------------------------------------------------
    # Text / UI
    # ------------------------------------------------------------------

    def draw_text(self, text: str, px: int, py: int, color: tuple | None = None) -> None:
        """Draw *text* at pixel coordinates (px, py)."""
        if color is None:
            color = self.UI_COLOR
        surf = self.font.render(text, True, color)
        self.screen.blit(surf, (px, py))

    def draw_hp_bar(
        self,
        px: int,
        py: int,
        width: int,
        height: int,
        hp: int,
        max_hp: int,
    ) -> None:
        ratio = max(0.0, hp / max_hp) if max_hp > 0 else 0.0
        pygame.draw.rect(self.screen, self.HP_BAR_BG, (px, py, width, height))
        pygame.draw.rect(self.screen, self.HP_BAR_FG, (px, py, int(width * ratio), height))
