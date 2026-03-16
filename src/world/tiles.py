"""
Tile type definitions and their sprite-sheet tile indices.
"""

from enum import IntEnum, auto


class TileType(IntEnum):
    WALL = auto()
    FLOOR = auto()
    STAIRS = auto()


# Maps TileType → tile index in the sprite atlas.
# Index 0 = first tile, laid out left-to-right, top-to-bottom.
# These values are used as fallback defaults; the authoritative mapping is
# in the "tiles" section of assets/sprites/atlas.json.
TILE_SPRITE: dict[TileType, int] = {
    TileType.WALL: 0,
    TileType.FLOOR: 1,
    TileType.STAIRS: 2,
}

# Which tile types can be walked on
WALKABLE: set[TileType] = {TileType.FLOOR, TileType.STAIRS}
