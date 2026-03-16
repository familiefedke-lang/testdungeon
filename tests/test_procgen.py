"""
Tests for procedural generation (procgen).
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import random
import pytest
from src.world.procgen import generate_floor, Room
from src.world.tiles import TileType
from src.ecs.entity import Actor
from src.constants import GRID_W, GRID_H


class TestRoom:
    def test_center(self):
        r = Room(0, 0, 4, 4)
        assert r.cx == 2
        assert r.cy == 2

    def test_intersects_overlapping(self):
        r1 = Room(0, 0, 5, 5)
        r2 = Room(3, 3, 5, 5)
        assert r1.intersects(r2, padding=0) is True

    def test_intersects_non_overlapping(self):
        r1 = Room(0, 0, 3, 3)
        r2 = Room(10, 10, 3, 3)
        assert r1.intersects(r2, padding=0) is False

    def test_floor_tiles_count(self):
        r = Room(0, 0, 3, 4)
        tiles = r.floor_tiles()
        assert len(tiles) == 12


class TestGenerateFloor:
    def test_returns_game_map_and_valid_start(self):
        rng = random.Random(42)
        game_map, sx, sy = generate_floor(floor=1, rng=rng)
        assert 0 <= sx < GRID_W
        assert 0 <= sy < GRID_H

    def test_start_tile_is_floor(self):
        rng = random.Random(42)
        game_map, sx, sy = generate_floor(floor=1, rng=rng)
        assert game_map.get_tile(sx, sy) == TileType.FLOOR

    def test_stairs_exist(self):
        rng = random.Random(42)
        game_map, sx, sy = generate_floor(floor=1, rng=rng)
        found = any(
            game_map.get_tile(x, y) == TileType.STAIRS
            for y in range(GRID_H)
            for x in range(GRID_W)
        )
        assert found is True

    def test_enemies_are_actors(self):
        rng = random.Random(42)
        game_map, sx, sy = generate_floor(floor=1, rng=rng)
        for entity in game_map.entities:
            assert isinstance(entity, Actor)

    def test_deterministic_with_same_seed(self):
        game_map1, sx1, sy1 = generate_floor(floor=1, rng=random.Random(99))
        game_map2, sx2, sy2 = generate_floor(floor=1, rng=random.Random(99))
        assert sx1 == sx2 and sy1 == sy2
        # Compare tile grids
        for y in range(GRID_H):
            for x in range(GRID_W):
                assert game_map1.get_tile(x, y) == game_map2.get_tile(x, y)

    def test_map_dimensions(self):
        rng = random.Random(1)
        game_map, _, _ = generate_floor(floor=1, rng=rng)
        assert len(game_map.tiles) == GRID_H
        assert len(game_map.tiles[0]) == GRID_W
