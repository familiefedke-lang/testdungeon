"""
Procedural dungeon generator.

Algorithm (room-and-corridor):
1. Start with all WALL.
2. Attempt to place random rectangular rooms.  Reject overlapping ones.
3. Carve each room to FLOOR, connect to previous room via L-shaped tunnel.
4. Place stairs in the last room.
5. Spawn enemies (0-2) in rooms other than the start room.

Returns (game_map, player_start_x, player_start_y).
"""

from __future__ import annotations

import random
from dataclasses import dataclass
from typing import TYPE_CHECKING

from src.constants import GRID_W, GRID_H
from src.world.game_map import GameMap
from src.world.tiles import TileType
from src.ecs.entity import Actor
from src.ecs.components.fighter import Fighter
from src.ecs.components.sprite import SpriteComponent
from src.ecs.components.ai import BasicAI

if TYPE_CHECKING:
    pass


# ---------------------------------------------------------------------------
# Room helper
# ---------------------------------------------------------------------------

@dataclass
class Room:
    x: int   # top-left tile
    y: int
    w: int
    h: int

    @property
    def cx(self) -> int:
        return self.x + self.w // 2

    @property
    def cy(self) -> int:
        return self.y + self.h // 2

    def intersects(self, other: "Room", padding: int = 1) -> bool:
        return (
            self.x - padding < other.x + other.w
            and self.x + self.w + padding > other.x
            and self.y - padding < other.y + other.h
            and self.y + self.h + padding > other.y
        )

    def floor_tiles(self) -> list[tuple[int, int]]:
        return [
            (self.x + dx, self.y + dy)
            for dx in range(self.w)
            for dy in range(self.h)
        ]


# ---------------------------------------------------------------------------
# Tunnel carving
# ---------------------------------------------------------------------------

def _carve_h_tunnel(game_map: GameMap, x1: int, x2: int, y: int) -> None:
    for x in range(min(x1, x2), max(x1, x2) + 1):
        game_map.set_tile(x, y, TileType.FLOOR)


def _carve_v_tunnel(game_map: GameMap, y1: int, y2: int, x: int) -> None:
    for y in range(min(y1, y2), max(y1, y2) + 1):
        game_map.set_tile(x, y, TileType.FLOOR)


# ---------------------------------------------------------------------------
# Main generator
# ---------------------------------------------------------------------------

def generate_floor(
    floor: int = 1,
    rng: random.Random | None = None,
) -> tuple[GameMap, int, int]:
    """
    Generate a new dungeon floor.

    Returns (game_map, start_x, start_y).
    Enemies are placed inside game_map.entities.
    """
    if rng is None:
        rng = random.Random()

    game_map = GameMap()

    max_rooms = 12
    min_room_size = 4
    max_room_size = 10

    rooms: list[Room] = []

    for _ in range(max_rooms):
        w = rng.randint(min_room_size, max_room_size)
        h = rng.randint(min_room_size, max_room_size)
        # Keep 1-tile border around map
        x = rng.randint(1, GRID_W - w - 2)
        y = rng.randint(1, GRID_H - h - 2)
        new_room = Room(x, y, w, h)

        if any(new_room.intersects(r) for r in rooms):
            continue

        # Carve room
        for rx, ry in new_room.floor_tiles():
            game_map.set_tile(rx, ry, TileType.FLOOR)

        # Connect to previous room
        if rooms:
            prev = rooms[-1]
            if rng.random() < 0.5:
                _carve_h_tunnel(game_map, prev.cx, new_room.cx, prev.cy)
                _carve_v_tunnel(game_map, prev.cy, new_room.cy, new_room.cx)
            else:
                _carve_v_tunnel(game_map, prev.cy, new_room.cy, prev.cx)
                _carve_h_tunnel(game_map, prev.cx, new_room.cx, new_room.cy)

        rooms.append(new_room)

    # Need at least one room
    if not rooms:
        # Fallback: single central room
        w, h = 10, 8
        x = GRID_W // 2 - w // 2
        y = GRID_H // 2 - h // 2
        fallback = Room(x, y, w, h)
        for rx, ry in fallback.floor_tiles():
            game_map.set_tile(rx, ry, TileType.FLOOR)
        rooms.append(fallback)

    # Player starts in centre of first room
    start_x, start_y = rooms[0].cx, rooms[0].cy

    # Stairs in last room (or random other room if >= 2 rooms)
    stair_room = rooms[-1] if len(rooms) < 2 else rng.choice(rooms[1:])
    stair_tiles = [
        (tx, ty) for tx, ty in stair_room.floor_tiles()
        if (tx, ty) != (start_x, start_y)
    ]
    if stair_tiles:
        sx, sy = rng.choice(stair_tiles)
        game_map.set_tile(sx, sy, TileType.STAIRS)

    # Spawn enemies in rooms other than start
    enemy_rooms = rooms[1:] if len(rooms) > 1 else []
    for room in enemy_rooms:
        count = rng.randint(0, 2)
        occupied: set[tuple[int, int]] = set()
        for _ in range(count):
            candidates = [
                (tx, ty) for tx, ty in room.floor_tiles()
                if game_map.get_tile(tx, ty) == TileType.FLOOR
                and (tx, ty) not in occupied
            ]
            if not candidates:
                break
            ex, ey = rng.choice(candidates)
            occupied.add((ex, ey))
            enemy = _make_enemy(ex, ey, floor, rng)
            game_map.entities.add(enemy)

    return game_map, start_x, start_y


def _make_enemy(x: int, y: int, floor: int, rng: random.Random) -> Actor:
    """Create a goblin enemy scaled (slightly) to the floor number."""
    hp = 8 + floor * 2
    power = 2 + floor
    return Actor(
        x, y,
        fighter=Fighter(hp=hp, power=power),
        sprite=SpriteComponent("goblin", anim="idle", facing="S"),
        ai=BasicAI(),
        name="goblin",
    )
