"""
Tests for Engine (turn resolution, without pygame rendering).
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import random
import pytest

# Stub out AnimationDB to avoid needing a real atlas.json in tests
from unittest.mock import MagicMock

from src.engine import Engine
from src.input.input_handler import Move, UseStairs, Quit
from src.world.tiles import TileType
from src.ecs.entity import Actor
from src.ecs.components.fighter import Fighter
from src.ecs.components.sprite import SpriteComponent


def _make_engine() -> Engine:
    anim_db = MagicMock()
    anim_db.get_frames.return_value = [0]
    anim_db.get_fps.return_value = 8.0
    engine = Engine(animation_db=anim_db)
    engine.new_game()
    return engine


class TestEngine:
    def test_new_game_creates_player(self):
        engine = _make_engine()
        assert engine.player is not None

    def test_new_game_creates_map(self):
        engine = _make_engine()
        assert engine.game_map is not None

    def test_floor_starts_at_one(self):
        engine = _make_engine()
        assert engine.floor == 1

    def test_move_to_floor_tile(self):
        engine = _make_engine()
        player = engine.player
        game_map = engine.game_map

        # Find a floor tile adjacent to player
        for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
            nx, ny = player.x + dx, player.y + dy
            if game_map.in_bounds(nx, ny) and game_map.get_tile(nx, ny) == TileType.FLOOR:
                old_x, old_y = player.x, player.y
                taken = engine.try_player_command(Move(dx, dy))
                assert taken is True
                assert (player.x, player.y) == (nx, ny)
                return
        pytest.skip("No adjacent floor tile found (unlikely but possible)")

    def test_move_into_wall_fails(self):
        engine = _make_engine()
        player = engine.player
        game_map = engine.game_map

        # Find a wall tile adjacent to player
        for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
            nx, ny = player.x + dx, player.y + dy
            if game_map.in_bounds(nx, ny) and game_map.get_tile(nx, ny) == TileType.WALL:
                old_x, old_y = player.x, player.y
                taken = engine.try_player_command(Move(dx, dy))
                assert taken is False
                assert (player.x, player.y) == (old_x, old_y)
                return
        pytest.skip("No adjacent wall tile found (unlikely but possible)")

    def test_quit_command_stops_running(self):
        engine = _make_engine()
        engine.try_player_command(Quit())
        assert engine.running is False

    def test_use_stairs_on_non_stair_fails(self):
        engine = _make_engine()
        player = engine.player
        game_map = engine.game_map
        # Player starts on a floor tile, not stairs
        assert game_map.get_tile(player.x, player.y) == TileType.FLOOR
        taken = engine.try_player_command(UseStairs())
        assert taken is False

    def test_use_stairs_advances_floor(self):
        engine = _make_engine()
        player = engine.player
        game_map = engine.game_map
        # Manually place player on a stairs tile
        game_map.set_tile(player.x, player.y, TileType.STAIRS)
        old_floor = engine.floor
        taken = engine.try_player_command(UseStairs())
        assert taken is True
        assert engine.floor == old_floor + 1

    def test_bump_attack_enemy(self):
        engine = _make_engine()
        player = engine.player
        game_map = engine.game_map

        # Place an enemy adjacent to player on a floor tile
        for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
            nx, ny = player.x + dx, player.y + dy
            if game_map.in_bounds(nx, ny) and game_map.get_tile(nx, ny) == TileType.FLOOR:
                enemy = Actor(
                    nx, ny,
                    fighter=Fighter(hp=100, power=0),
                    sprite=SpriteComponent("goblin"),
                    name="dummy",
                )
                game_map.entities.add(enemy)
                taken = engine.try_player_command(Move(dx, dy))
                assert taken is True
                assert enemy.fighter.hp < 100  # took damage
                return
        pytest.skip("No adjacent floor tile for enemy placement")
