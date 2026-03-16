"""
Tests for SpriteComponent.
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from src.ecs.components.sprite import SpriteComponent


class TestSpriteComponent:
    def test_initial_state(self):
        s = SpriteComponent("player", anim="idle", facing="S")
        assert s.anim == "idle"
        assert s.facing == "S"

    def test_play_changes_anim(self):
        s = SpriteComponent("player")
        s.play("walk")
        assert s.anim == "walk"

    def test_play_resets_frame_on_new_anim(self):
        s = SpriteComponent("player")
        s._frame_index = 2
        s.play("walk")
        assert s._frame_index == 0

    def test_lock_prevents_auto_return_to_idle(self):
        s = SpriteComponent("player")
        s.play("attack", lock_for=0.5)
        s.update(0.2)  # still locked
        assert s.anim == "attack"

    def test_lock_expires_returns_to_idle(self):
        s = SpriteComponent("player")
        s.play("attack", lock_for=0.1)
        s.update(0.2)  # lock should have expired
        assert s.anim == "idle"

    def test_dead_animation_never_returns_to_idle(self):
        s = SpriteComponent("player")
        s.play("dead", lock_for=999.0)
        # Simulate many frames
        for _ in range(100):
            s.update(0.1)
        assert s.anim == "dead"

    def test_set_facing_from_delta_east(self):
        s = SpriteComponent("player")
        s.set_facing_from_delta(1, 0)
        assert s.facing == "E"

    def test_set_facing_from_delta_west(self):
        s = SpriteComponent("player")
        s.set_facing_from_delta(-1, 0)
        assert s.facing == "W"

    def test_set_facing_from_delta_north(self):
        s = SpriteComponent("player")
        s.set_facing_from_delta(0, -1)
        assert s.facing == "N"

    def test_set_facing_from_delta_south(self):
        s = SpriteComponent("player")
        s.set_facing_from_delta(0, 1)
        assert s.facing == "S"
