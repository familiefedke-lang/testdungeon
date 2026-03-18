from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class ItemDef:
    key: str
    name: str
    sprite: str
    stackable: bool
    equip_slot: str | None
    bonuses: dict[str, int]


class ItemsDB:
    def __init__(self, path: str) -> None:
        raw = json.loads(Path(path).read_text(encoding="utf-8"))
        self._items: dict[str, ItemDef] = {}

        for key, data in raw.items():
            key_l = key.lower()
            name = str(data.get("name", key))
            sprite = str(data.get("sprite", key))
            stackable = bool(data.get("stackable", False))

            equip = data.get("equip")
            equip_slot: str | None = None
            bonuses: dict[str, int] = {}
            if isinstance(equip, dict):
                equip_slot = str(equip.get("slot")) if equip.get("slot") is not None else None
                b = equip.get("bonuses", {})
                if isinstance(b, dict):
                    bonuses = {str(k): int(v) for k, v in b.items()}

            self._items[key_l] = ItemDef(
                key=key_l,
                name=name,
                sprite=sprite,
                stackable=stackable,
                equip_slot=equip_slot,
                bonuses=bonuses,
            )

    def get(self, key: str) -> ItemDef | None:
        return self._items.get(key.lower())

    def require(self, key: str) -> ItemDef:
        item = self.get(key)
        if item is None:
            raise KeyError(f"Unknown item key: {key}")
        return item