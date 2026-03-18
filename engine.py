from __future__ import annotations

import os
from typing import TYPE_CHECKING

from src.constants import GRID_W, GRID_H, WINDOW_H
from src.world.tiles import TileType
from src.world.procgen import generate_floor
from src.ecs.entity import Actor
from src.ecs.item import Item
from src.ecs.components.fighter import Fighter
from src.ecs.components.sprite import SpriteComponent
from src.input.input_handler import Move, UseStairs, Pickup, Quit, Command
from src.data.items_db import ItemsDB

if TYPE_CHECKING:
    from src.world.game_map import GameMap
    from src.render.renderer import Renderer
    from src.render.animations import AnimationDB


class Engine:
    # Old MAX_MESSAGES was 6; console window wants more history
    MAX_MESSAGES = 200

    def __init__(self, animation_db: "AnimationDB") -> None:
        self.animation_db = animation_db
        self.game_map: "GameMap | None" = None
        self.player: "Actor | None" = None
        self.floor: int = 0
        self.messages: list[str] = []
        self.running: bool = True

        repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        items_path = os.path.join(repo_root, "assets", "data", "items.json")
        self.items_db = ItemsDB(items_path)

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
    # Derived stat helpers
    # ------------------------------------------------------------------

    def _equipment_bonuses(self, actor: Actor) -> dict[str, int]:
        bonuses: dict[str, int] = {}
        for _, item_key in actor.equipment.slots.items():
            item_def = self.items_db.get(item_key)
            if item_def is None:
                continue
            for stat, value in item_def.bonuses.items():
                bonuses[stat] = bonuses.get(stat, 0) + int(value)
        return bonuses

    def _armor(self, actor: Actor) -> int:
        return int(self._equipment_bonuses(actor).get("armor", 0))

    def _power(self, actor: Actor) -> int:
        base = actor.fighter.base_power
        bonus = int(self._equipment_bonuses(actor).get("power", 0))
        return base + bonus

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
        if isinstance(cmd, Quit):
            self.running = False
            return False

        if self.player is not None and not self.player.is_alive:
            return False

        assert self.player is not None and self.game_map is not None

        if isinstance(cmd, Move):
            return self._handle_move(cmd.dx, cmd.dy)

        if isinstance(cmd, UseStairs):
            return self._handle_use_stairs()

        if isinstance(cmd, Pickup):
            return self._handle_pickup()

        return False

    def _handle_move(self, dx: int, dy: int) -> bool:
        player = self.player
        assert player is not None and self.game_map is not None

        nx, ny = player.x + dx, player.y + dy

        if not self.game_map.in_bounds(nx, ny):
            return False

        target = self.game_map.actor_at(nx, ny)
        if target is not None:
            atk_power = self._power(player)
            tgt_armor = self._armor(target)
            damage = max(0, atk_power - tgt_armor)

            dealt = player.fighter.attack(target, damage)
            self._log(f"You attack {target.name} for {dealt} damage.")
            if target.fighter.is_dead:
                self._log(f"{target.name} dies.")
                self._remove_dead()
            player.sprite.set_facing_from_delta(dx, dy)
            return True

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

    def _handle_pickup(self) -> bool:
        assert self.player is not None and self.game_map is not None
        px, py = self.player.x, self.player.y

        found: Item | None = None
        for e in self.game_map.entities:
            if isinstance(e, Item) and e.x == px and e.y == py:
                found = e
                break

        if found is None:
            self._log("Nothing here to pick up.")
            return False

        self.game_map.entities.remove(found)
        self.player.inventory.add(found.item_key)

        item_def = self.items_db.get(found.item_key)
        if item_def is not None and item_def.equip_slot is not None:
            if self.player.equipment.equip(item_def.equip_slot, found.item_key):
                self._log(f"You pick up and equip {item_def.name}.")
                return True

        self._log(f"You pick up {found.name}.")
        return True

    def enemy_turns(self) -> None:
        assert self.game_map is not None and self.player is not None
        if not self.player.is_alive:
            return

        for entity in list(self.game_map.entities):
            if not isinstance(entity, Actor):
                continue
            if not entity.is_alive or entity.ai is None:
                continue
            entity.ai.take_turn(self.player, self.game_map)
            if not self.player.is_alive:
                self._log("You die!")
                self.running = False
                break

        self._remove_dead()

    # ------------------------------------------------------------------
    # Rendering
    # ------------------------------------------------------------------

    def render(self, renderer: "Renderer") -> None:
        assert self.game_map is not None and self.player is not None

        renderer.clear()

        for y in range(GRID_H):
            for x in range(GRID_W):
                renderer.draw_tile(self.game_map.get_tile(x, y), x, y)

        drawables = list(self.game_map.entities) + [self.player]
        drawables.sort(key=lambda e: getattr(e, "render_layer", 0))

        for e in drawables:
            if isinstance(e, Item):
                renderer.draw_item(e)
            elif isinstance(e, Actor):
                renderer.draw_actor(e)

        self._render_ui(renderer)

    def _render_ui(self, renderer: "Renderer") -> None:
        assert self.player is not None

        # --- top-left status ---
        f = self.player.fighter
        renderer.draw_text(f"HP: {f.hp}/{f.max_hp}", 8, 8)
        renderer.draw_hp_bar(8, 28, 140, 10, f.hp, f.max_hp)
        renderer.draw_text(f"Floor: {self.floor}", 8, 44)
        renderer.draw_text(f"Power: {self._power(self.player)}", 8, 60)
        renderer.draw_text(f"Armor: {self._armor(self.player)}", 8, 76)

        # --- bottom-left console window ---
        # Panel geometry (px)
        panel_x = 8
        panel_h = 220
        panel_w = 520
        panel_y = WINDOW_H - panel_h - 8

        renderer.draw_panel(panel_x, panel_y, panel_w, panel_h, bg=(0, 0, 0), alpha=170)

        # Text layout inside panel
        padding = 8
        line_h = 16
        max_lines = (panel_h - 2 * padding) // line_h

        lines = self.messages[-max_lines:]
        y = panel_y + padding
        for msg in lines:
            renderer.draw_text(msg, panel_x + padding, y, color=(230, 230, 210))
            y += line_h

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _remove_dead(self) -> None:
        assert self.game_map is not None
        self.game_map.entities = [
            e for e in self.game_map.entities
            if not (isinstance(e, Actor) and not e.is_alive)
        ]

    def _log(self, message: str) -> None:
        self.messages.append(message)
        if len(self.messages) > self.MAX_MESSAGES:
            self.messages = self.messages[-self.MAX_MESSAGES:]