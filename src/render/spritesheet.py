"""
Spritesheet – loads atlas.png and exposes 32×32 tile surfaces by index.
"""

from __future__ import annotations

import pygame


class Spritesheet:
    def __init__(self, path: str, tile_size: int = 32, tiles_per_row: int = 8) -> None:
        self.tile_size: int = tile_size
        self.tiles_per_row: int = tiles_per_row
        raw = pygame.image.load(path)
        try:
            self._sheet: pygame.Surface = raw.convert_alpha()
        except pygame.error:
            # No display mode set (e.g. headless / testing); use surface as-is.
            self._sheet = raw
        self._cache: dict[int, pygame.Surface] = {}

    def get_tile_surface(self, tile_index: int) -> pygame.Surface:
        """Return a 32×32 Surface for *tile_index* (0-based, left-to-right, top-to-bottom)."""
        if tile_index in self._cache:
            return self._cache[tile_index]

        t = self.tile_size
        col = tile_index % self.tiles_per_row
        row = tile_index // self.tiles_per_row
        rect = pygame.Rect(col * t, row * t, t, t)
        surface = pygame.Surface((t, t), pygame.SRCALPHA)
        surface.blit(self._sheet, (0, 0), rect)
        self._cache[tile_index] = surface
        return surface
