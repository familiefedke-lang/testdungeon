from __future__ import annotations

import json


class ItemsAtlas:
    def __init__(self, path: str) -> None:
        with open(path, "r") as fh:
            data: dict = json.load(fh)

        self.tile_size: int = int(data.get("tileSize", 32))
        self.tiles_per_row: int = int(data.get("tilesPerRow", 3))
        self._items: dict[str, int] = {k.lower(): int(v) for k, v in data.get("items", {}).items()}

    def get_item_index(self, item_key: str, default: int = 0) -> int:
        return self._items.get(item_key.lower(), default)