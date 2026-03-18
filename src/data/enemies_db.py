from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class EnemyScaling:
    hp_per_floor: int = 0
    power_per_floor: int = 0


@dataclass(frozen=True)
class EnemyDef:
    key: str
    name: str
    sprite: str
    ai: str
    base_hp: int
    base_power: int
    scaling: EnemyScaling


class EnemiesDB:
    """
    Loads enemies from assets/data/enemies.json and can instantiate Actors.

    Expected schema:
    {
      "goblin": {
        "name": "goblin",
        "sprite": "goblin",
        "ai": "basic",
        "fighter": {"hp": 8, "power": 2},
        "scaling": {"hp_per_floor": 2, "power_per_floor": 1}
      }
    }
    """

    def __init__(self, path: str) -> None:
        raw = json.loads(Path(path).read_text(encoding="utf-8"))
        self._enemies: dict[str, EnemyDef] = {}

        for key, data in raw.items():
            key_l = str(key).lower()
            name = str(data.get("name", key_l))
            sprite = str(data.get("sprite", key_l))
            ai = str(data.get("ai", "basic")).lower()

            fighter = data.get("fighter", {})
            base_hp = int(fighter.get("hp", 1))
            base_power = int(fighter.get("power", 1))

            scaling_raw = data.get("scaling", {}) or {}
            scaling = EnemyScaling(
                hp_per_floor=int(scaling_raw.get("hp_per_floor", 0)),
                power_per_floor=int(scaling_raw.get("power_per_floor", 0)),
            )

            self._enemies[key_l] = EnemyDef(
                key=key_l,
                name=name,
                sprite=sprite,
                ai=ai,
                base_hp=base_hp,
                base_power=base_power,
                scaling=scaling,
            )

    def get(self, key: str) -> EnemyDef | None:
        return self._enemies.get(key.lower())

    def require(self, key: str) -> EnemyDef:
        e = self.get(key)
        if e is None:
            raise KeyError(f"Unknown enemy key: {key}")
        return e

    def create_actor(self, enemy_key: str, x: int, y: int, *, floor: int) -> "Actor":
        """
        Instantiate an Actor for the given enemy type at (x, y).
        Scaling is applied as:
          stat = base + floor * per_floor
        """
        from src.ecs.entity import Actor
        from src.ecs.components.fighter import Fighter
        from src.ecs.components.sprite import SpriteComponent
        from src.ecs.components.ai import BasicAI

        e = self.require(enemy_key)

        hp = e.base_hp + floor * e.scaling.hp_per_floor
        power = e.base_power + floor * e.scaling.power_per_floor

        # AI selector (extend later)
        ai_obj = None
        if e.ai == "basic":
            ai_obj = BasicAI()
        else:
            # Fallback
            ai_obj = BasicAI()

        return Actor(
            x, y,
            fighter=Fighter(hp=hp, power=power),
            sprite=SpriteComponent(e.sprite, anim="idle", facing="S"),
            ai=ai_obj,
            name=e.name,
        )