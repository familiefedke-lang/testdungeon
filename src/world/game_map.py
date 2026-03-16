"""
GameMap – owns the 50×30 tile grid and entity set for a single floor.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from src.constants import GRID_W, GRID_H
from src.world.tiles import TileType, WALKABLE

if TYPE_CHECKING:
    from src.ecs.entity import Entity, Actor


class GameMap:
    def __init__(self) -> None:
        # 2-D tile array: tiles[y][x]
        self.tiles: list[list[TileType]] = [
            [TileType.WALL] * GRID_W for _ in range(GRID_H)
        ]
        # All entities currently on this floor (excludes the player,
        # which is tracked separately in Engine).
        self.entities: set[Entity] = set()

    # ------------------------------------------------------------------
    # Bounds helpers
    # ------------------------------------------------------------------

    def in_bounds(self, x: int, y: int) -> bool:
        return 0 <= x < GRID_W and 0 <= y < GRID_H

    def get_tile(self, x: int, y: int) -> TileType:
        return self.tiles[y][x]

    def set_tile(self, x: int, y: int, tile: TileType) -> None:
        self.tiles[y][x] = tile

    # ------------------------------------------------------------------
    # Walkability
    # ------------------------------------------------------------------

    def is_walkable(self, x: int, y: int) -> bool:
        """True if (x, y) is in bounds, tile is walkable, and no blocking entity occupies it."""
        if not self.in_bounds(x, y):
            return False
        if self.tiles[y][x] not in WALKABLE:
            return False
        return self.blocking_entity_at(x, y) is None

    # ------------------------------------------------------------------
    # Entity lookups
    # ------------------------------------------------------------------

    def blocking_entity_at(self, x: int, y: int) -> "Entity | None":
        for e in self.entities:
            if e.blocks and e.x == x and e.y == y:
                return e
        return None

    def actor_at(self, x: int, y: int) -> "Actor | None":
        from src.ecs.entity import Actor
        for e in self.entities:
            if isinstance(e, Actor) and e.x == x and e.y == y:
                return e
        return None
