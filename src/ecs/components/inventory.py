from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class InventoryComponent:
    """
    Minimal inventory: list of item keys.
    """
    items: list[str] = field(default_factory=list)

    def add(self, item_key: str) -> None:
        self.items.append(item_key)