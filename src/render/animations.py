"""
AnimationDB – loads animation frame-list definitions from atlas.json
and provides frame lookups for the renderer and SpriteComponent.

Expected atlas.json schema
--------------------------
{
  "tileSize": 32,
  "tilesPerRow": <int>,
  "defaultFps": 8,
  "sprites": {
    "<sprite_key>": {
      "<anim_name>": {
        "<facing>": [<tile_index>, ...],
        "fps": <optional float>
      }
    }
  }
}

Facing keys: "N", "S", "E", "W".
If a specific facing is absent the implementation falls back to "S".
"""

from __future__ import annotations

import json
import os


class AnimationDB:
    def __init__(self, path: str) -> None:
        with open(path, "r") as fh:
            data: dict = json.load(fh)

        self.tile_size: int = data.get("tileSize", 32)
        self.tiles_per_row: int = data.get("tilesPerRow", 8)
        self.default_fps: float = float(data.get("defaultFps", 8.0))
        # tile_sprites["wall"] = 0, ["floor"] = 1, etc.
        self._tile_sprites: dict[str, int] = {
            k.lower(): int(v) for k, v in data.get("tiles", {}).items()
        }
        # sprites[sprite_key][anim][facing] = list[int]
        self._db: dict[str, dict[str, dict[str, list[int]]]] = {}
        # fps overrides per (sprite_key, anim)
        self._fps: dict[tuple[str, str], float] = {}

        for sprite_key, anims in data.get("sprites", {}).items():
            self._db[sprite_key] = {}
            for anim_name, facing_data in anims.items():
                if anim_name == "fps":
                    continue
                self._db[sprite_key][anim_name] = {}
                anim_fps = float(facing_data.get("fps", self.default_fps))
                self._fps[(sprite_key, anim_name)] = anim_fps
                for facing, frames in facing_data.items():
                    if facing == "fps":
                        continue
                    self._db[sprite_key][anim_name][facing] = frames

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def get_frames(self, sprite_key: str, anim: str, facing: str = "S") -> list[int]:
        """Return list of atlas tile indices for the given sprite/anim/facing.

        Falls back gracefully: facing → "S" → first facing → [0].
        """
        sprite_db = self._db.get(sprite_key)
        if sprite_db is None:
            return [0]
        anim_db = sprite_db.get(anim)
        if anim_db is None:
            anim_db = sprite_db.get("idle", {})
        if not anim_db:
            return [0]
        if facing in anim_db:
            return anim_db[facing]
        if "S" in anim_db:
            return anim_db["S"]
        # Return first available facing
        return next(iter(anim_db.values()), [0])

    def get_fps(self, sprite_key: str, anim: str) -> float:
        return self._fps.get((sprite_key, anim), self.default_fps)

    def get_tile_sprite(self, tile_name: str, default: int = 0) -> int:
        """Return the atlas tile index for a map tile type name (e.g. "wall", "floor", "stairs").

        Falls back to *default* when the name is not found in the ``tiles`` section of atlas.json.
        """
        return self._tile_sprites.get(tile_name.lower(), default)
