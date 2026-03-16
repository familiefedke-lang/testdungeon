"""
Tests for AnimationDB – including the tiles section.
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
import tempfile
import pytest

from src.render.animations import AnimationDB


def _make_db(data: dict) -> AnimationDB:
    """Write *data* to a temp file and return an AnimationDB loaded from it."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as fh:
        json.dump(data, fh)
        path = fh.name
    return AnimationDB(path)


class TestAnimationDBTileSprites:
    def test_tile_sprites_loaded_from_atlas(self):
        db = _make_db({
            "tileSize": 32, "tilesPerRow": 8, "defaultFps": 6,
            "tiles": {"wall": 0, "floor": 1, "stairs": 2},
            "sprites": {},
        })
        assert db.get_tile_sprite("wall") == 0
        assert db.get_tile_sprite("floor") == 1
        assert db.get_tile_sprite("stairs") == 2

    def test_tile_names_are_case_insensitive(self):
        db = _make_db({
            "tileSize": 32, "tilesPerRow": 8, "defaultFps": 6,
            "tiles": {"Wall": 5, "FLOOR": 7},
            "sprites": {},
        })
        assert db.get_tile_sprite("wall") == 5
        assert db.get_tile_sprite("FLOOR") == 7
        assert db.get_tile_sprite("Floor") == 7

    def test_missing_tile_returns_default(self):
        db = _make_db({
            "tileSize": 32, "tilesPerRow": 8, "defaultFps": 6,
            "tiles": {"wall": 0},
            "sprites": {},
        })
        assert db.get_tile_sprite("unknown") == 0          # built-in default
        assert db.get_tile_sprite("unknown", 99) == 99     # caller-supplied default

    def test_no_tiles_section_returns_default(self):
        db = _make_db({
            "tileSize": 32, "tilesPerRow": 8, "defaultFps": 6,
            "sprites": {},
        })
        assert db.get_tile_sprite("wall") == 0
        assert db.get_tile_sprite("floor", 3) == 3

    def test_custom_tile_index(self):
        db = _make_db({
            "tileSize": 32, "tilesPerRow": 8, "defaultFps": 6,
            "tiles": {"wall": 10, "floor": 11, "stairs": 12},
            "sprites": {},
        })
        assert db.get_tile_sprite("wall") == 10
        assert db.get_tile_sprite("stairs") == 12
