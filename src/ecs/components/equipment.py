from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class EquipmentComponent:
    """
    Holds equipped item keys per slot.

    Slots are free-form strings ("head", "body", "weapon", ...).
    """
    slots: dict[str, str] = field(default_factory=dict)

    def equipped_item(self, slot: str) -> str | None:
        return self.slots.get(slot)

    def can_equip(self, slot: str) -> bool:
        return slot not in self.slots

    def equip(self, slot: str, item_key: str) -> bool:
        """Equip item_key into slot if empty. Returns True if equipped."""
        if slot in self.slots:
            return False
        self.slots[slot] = item_key
        return True