"""
Engine – owns the current run state and drives turn resolution.

Fields
------
  game_map  : GameMap       current floor's tile grid + enemy entities
  player    : Actor         the player entity
  floor     : int           current floor number (1-based)
  messages  : list[str]     recent log messages

Turn resolution
---------------
  try_player_command(cmd) → bool   process one player command, returns True if a turn passed
  enemy_turns()                    each living enemy takes its turn
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from src.constants import GRID_W, GRID_H
from src.world.tiles import TileType
from src.world.procgen import generate_floor
from src.ecs.entity import Actor
from src.ecs.components.fighter import Fighter
from src.ecs.components.sprite import SpriteComponent
from src.input.input_handler import Move, UseStairs, Quit, Command

if TYPE_CHECKING:
    from src.world.game_map import GameMap
    from src.render.renderer import Renderer
    from src.render.animations import AnimationDB


class Engine:
    MAX_MESSAGES = 6

    def __init__(self, animation_db: "AnimationDB") -> None:
        self.animation_db = animation_db
        self.game_map: "GameMap | None" = None
        self.player: "Actor | None" = None
        self.floor: int = 0
        self.messages: list[str] = []
        self.running: bool = True

    # ------------------------------------------------------------------
    # Setup
    # ------------------------------------------------------------------

    def new_game(self) -> None:
        self.floor = 0
        self.messages.clear()
        self._next_floor()

    def _next_floor(self) -> None:
        self.floor += 1
        game_map, sx, sy = generate_floor(floor=self.floor)
        self.game_map = game_map

        if self.player is None:
            self.player = Actor(
                sx, sy,
                fighter=Fighter(hp=30, power=5),
                sprite=SpriteComponent("player", anim="idle", facing="S"),
                ai=None,
                name="player",
            )
        else:
            self.player.x = sx
            self.player.y = sy

        self._log(f"You descend to floor {self.floor}.")

    # ------------------------------------------------------------------
    # Per-frame update (animations)
    # ------------------------------------------------------------------

    def update(self, dt: float) -> None:
        if self.player is not None:
            self.player.sprite.update(dt, self.animation_db)
        if self.game_map is not None:
            for entity in list(self.game_map.entities):
                if isinstance(entity, Actor) and entity.sprite is not None:
                    entity.sprite.update(dt, self.animation_db)

    # ------------------------------------------------------------------
    # Turn resolution
    # ------------------------------------------------------------------

    def try_player_command(self, cmd: Command) -> bool:
        """Process a player command. Returns True if a full game-turn passed."""
        if isinstance(cmd, Quit):
            self.running = False
            return False

        # Don't process commands if the player is dead
        if self.player is not None and not self.player.is_alive:
            return False

        assert self.player is not None and self.game_map is not None

        if isinstance(cmd, Move):
            return self._handle_move(cmd.dx, cmd.dy)

        if isinstance(cmd, UseStairs):
            return self._handle_use_stairs()

        return False

    def _handle_move(self, dx: int, dy: int) -> bool:
        player = self.player
        assert player is not None and self.game_map is not None

        nx, ny = player.x + dx, player.y + dy

        if not self.game_map.in_bounds(nx, ny):
            return False

        # Bump-attack
        target = self.game_map.actor_at(nx, ny)
        if target is not None:
            damage = player.fighter.attack(target)
            self._log(f"You hit {target.name} for {damage} damage.")
            if target.fighter.is_dead:
                self._log(f"{target.name} is dead!")
                self._remove_dead()
            player.sprite.set_facing_from_delta(dx, dy)
            return True

        # Move
        if self.game_map.is_walkable(nx, ny):
            player.x = nx
            player.y = ny
            player.sprite.set_facing_from_delta(dx, dy)
            player.sprite.play("walk", lock_for=0.12)
            return True

        return False

    def _handle_use_stairs(self) -> bool:
        player = self.player
        assert player is not None and self.game_map is not None

        tile = self.game_map.get_tile(player.x, player.y)
        if tile == TileType.STAIRS:
            self._next_floor()
            return True
        return False

    def enemy_turns(self) -> None:
        assert self.game_map is not None and self.player is not None
        # Skip if player already dead
        if not self.player.is_alive:
            return
        for entity in list(self.game_map.entities):
            if not isinstance(entity, Actor):
                continue
            if not entity.is_alive or entity.ai is None:
                continue
            entity.ai.take_turn(self.player, self.game_map)
            if not self.player.is_alive:
                self._log("You died!")
                self.running = False
                break
        self._remove_dead()

    # ------------------------------------------------------------------
    # Rendering
    # ------------------------------------------------------------------

    def render(self, renderer: "Renderer") -> None:
        assert self.game_map is not None and self.player is not None

        renderer.clear()

        # Draw map tiles
        from src.constants import GRID_W, GRID_H
        for y in range(GRID_H):
            for x in range(GRID_W):
                renderer.draw_tile(self.game_map.get_tile(x, y), x, y)

        # Draw entities (sorted by render_layer)
        all_actors: list[Actor] = [
            e for e in self.game_map.entities if isinstance(e, Actor)
        ]
        all_actors.append(self.player)
        all_actors.sort(key=lambda a: a.render_layer)
        for actor in all_actors:
            renderer.draw_actor(actor)

        # UI overlay
        self._render_ui(renderer)

    def _render_ui(self, renderer: "Renderer") -> None:
        assert self.player is not None
        f = self.player.fighter
        renderer.draw_text(f"HP: {f.hp}/{f.max_hp}", 8, 8)
        renderer.draw_hp_bar(8, 28, 120, 10, f.hp, f.max_hp)
        renderer.draw_text(f"Floor: {self.floor}", 8, 44)

        # Message log
        y_offset = 60
        for msg in self.messages[-self.MAX_MESSAGES:]:
            renderer.draw_text(msg, 8, y_offset, color=(200, 200, 150))
            y_offset += 16

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _remove_dead(self) -> None:
        assert self.game_map is not None
        dead = {
            e for e in self.game_map.entities
            if isinstance(e, Actor) and not e.is_alive
        }
        self.game_map.entities -= dead

    def _log(self, message: str) -> None:
        self.messages.append(message)
        if len(self.messages) > 100:
            self.messages = self.messages[-100:]
