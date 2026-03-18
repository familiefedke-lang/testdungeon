"""
Entity classes for the ECS.

Entity  – base: position, blocking flag, render layer
Actor   – Entity + Fighter + SpriteComponent + optional AI + inventory/equipment
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from src.ecs.components.inventory import InventoryComponent
from src.ecs.components.equipment import EquipmentComponent

if TYPE_CHECKING:
    from src.ecs.components.fighter import Fighter
    from src.ecs.components.sprite import SpriteComponent
    from src.ecs.components.ai import BasicAI


class Entity:
    """A game object that occupies a tile position."""

    def __init__(
        self,
        x: int,
        y: int,
        *,
        blocks: bool = False,
        render_layer: int = 2,
        name: str = "entity",
    ) -> None:
        self.x: int = x
        self.y: int = y
        self.blocks: bool = blocks
        self.render_layer: int = render_layer
        self.name: str = name


class Actor(Entity):
    """An entity that can fight, animate, and (optionally) think."""

    def __init__(
        self,
        x: int,
        y: int,
        fighter: "Fighter",
        sprite: "SpriteComponent",
        ai: "BasicAI | None" = None,
        *,
        name: str = "actor",
        render_layer: int = 2,
    ) -> None:
        super().__init__(x, y, blocks=True, render_layer=render_layer, name=name)
        self.fighter: Fighter = fighter
        self.fighter.owner = self
        self.sprite: SpriteComponent = sprite
        self.ai: "BasicAI | None" = ai
        if ai is not None:
            ai.owner = self

        # New: inventory + equipment
        self.inventory = InventoryComponent()
        self.equipment = EquipmentComponent()

    @property
    def is_alive(self) -> bool:
        return not self.fighter.is_dead