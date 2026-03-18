from __future__ import annotations

from src.ecs.entity import Entity


class Item(Entity):
    """
    Ground item entity.

    - blocks=False so actors can stand on it.
    - render_layer=1 so it draws underneath actors.
    """
    def __init__(self, x: int, y: int, *, item_key: str, name: str | None = None) -> None:
        super().__init__(x, y, blocks=False, render_layer=1, name=name or item_key)
        self.item_key = item_key