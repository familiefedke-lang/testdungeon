"""
AI component – minimal hostile AI.

Each turn the enemy either:
  - attacks the player if adjacent (distance-1 Chebyshev), or
  - moves one step closer to the player (greedy, Manhattan distance).
"""

from __future__ import annotations

import math
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.ecs.entity import Actor
    from src.world.game_map import GameMap


class BasicAI:
    def __init__(self) -> None:
        self.owner: "Actor | None" = None  # set by Actor.__init__

    def take_turn(self, player: "Actor", game_map: "GameMap") -> None:
        if self.owner is None:
            return
        enemy = self.owner

        dx = player.x - enemy.x
        dy = player.y - enemy.y

        # Adjacent: Chebyshev distance == 1  (diagonal counts)
        if max(abs(dx), abs(dy)) <= 1:
            enemy.fighter.attack(player)
            return

        # Greedy step toward player
        step_x = int(math.copysign(1, dx)) if dx != 0 else 0
        step_y = int(math.copysign(1, dy)) if dy != 0 else 0

        # Try straight line first, then axis-only fallbacks
        candidates = [
            (step_x, step_y),
            (step_x, 0),
            (0, step_y),
        ]
        for sx, sy in candidates:
            nx, ny = enemy.x + sx, enemy.y + sy
            if game_map.is_walkable(nx, ny):
                enemy.x = nx
                enemy.y = ny
                if enemy.sprite is not None:
                    enemy.sprite.set_facing_from_delta(sx, sy)
                    enemy.sprite.play("walk", lock_for=0.12)
                return
