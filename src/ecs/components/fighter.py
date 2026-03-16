"""
Fighter component – owns HP and melee stats for an Actor.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.ecs.entity import Actor


class Fighter:
    def __init__(self, hp: int, power: int) -> None:
        self.max_hp: int = hp
        self.hp: int = hp
        self.power: int = power
        self.owner: "Actor | None" = None  # set by Actor.__init__

    @property
    def is_dead(self) -> bool:
        return self.hp <= 0

    def take_damage(self, amount: int) -> bool:
        """Apply *amount* damage. Returns True if the actor just died."""
        self.hp = max(0, self.hp - amount)
        if self.owner is not None and self.owner.sprite is not None:
            if self.is_dead:
                self.owner.sprite.play("dead", lock_for=999.0)
            else:
                self.owner.sprite.play("hurt", lock_for=0.10)
        return self.is_dead

    def attack(self, target: "Actor") -> int:
        """Attack *target*, dealing self.power damage. Returns damage dealt."""
        damage = self.power
        target.fighter.take_damage(damage)
        if self.owner is not None and self.owner.sprite is not None:
            self.owner.sprite.play("attack", lock_for=0.15)
        return damage
