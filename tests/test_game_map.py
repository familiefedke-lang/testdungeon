"""
Tests for world/game_map.py.
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from src.world.game_map import GameMap
from src.world.tiles import TileType
from src.ecs.entity import Actor, Entity
from src.ecs.components.fighter import Fighter
from src.ecs.components.sprite import SpriteComponent


def _make_actor(x: int, y: int) -> Actor:
    return Actor(x, y, fighter=Fighter(hp=10, power=1), sprite=SpriteComponent("goblin"))


class TestGameMap:
    def setup_method(self):
        self.gm = GameMap()

    def test_default_tiles_are_wall(self):
        assert self.gm.get_tile(0, 0) == TileType.WALL
        assert self.gm.get_tile(25, 15) == TileType.WALL

    def test_set_and_get_tile(self):
        self.gm.set_tile(5, 5, TileType.FLOOR)
        assert self.gm.get_tile(5, 5) == TileType.FLOOR

    def test_in_bounds_valid(self):
        assert self.gm.in_bounds(0, 0) is True
        assert self.gm.in_bounds(49, 29) is True

    def test_in_bounds_invalid(self):
        assert self.gm.in_bounds(-1, 0) is False
        assert self.gm.in_bounds(50, 0) is False
        assert self.gm.in_bounds(0, 30) is False

    def test_is_walkable_floor(self):
        self.gm.set_tile(3, 3, TileType.FLOOR)
        assert self.gm.is_walkable(3, 3) is True

    def test_is_walkable_wall(self):
        assert self.gm.is_walkable(2, 2) is False  # default is WALL

    def test_is_walkable_blocked_by_entity(self):
        self.gm.set_tile(4, 4, TileType.FLOOR)
        actor = _make_actor(4, 4)
        self.gm.entities.add(actor)
        assert self.gm.is_walkable(4, 4) is False

    def test_actor_at_returns_actor(self):
        self.gm.set_tile(6, 6, TileType.FLOOR)
        actor = _make_actor(6, 6)
        self.gm.entities.add(actor)
        assert self.gm.actor_at(6, 6) is actor

    def test_actor_at_returns_none(self):
        assert self.gm.actor_at(1, 1) is None

    def test_blocking_entity_at(self):
        actor = _make_actor(7, 7)
        self.gm.entities.add(actor)
        assert self.gm.blocking_entity_at(7, 7) is actor
        assert self.gm.blocking_entity_at(8, 8) is None
