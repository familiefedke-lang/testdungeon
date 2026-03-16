"""
Tests for fighter component.
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from src.ecs.components.fighter import Fighter
from src.ecs.components.sprite import SpriteComponent
from src.ecs.entity import Actor


def _make_actor(hp: int = 10, power: int = 3) -> Actor:
    return Actor(
        0, 0,
        fighter=Fighter(hp=hp, power=power),
        sprite=SpriteComponent("player"),
        name="test",
    )


class TestFighter:
    def test_initial_hp(self):
        a = _make_actor(hp=10)
        assert a.fighter.hp == 10
        assert a.fighter.max_hp == 10

    def test_take_damage_reduces_hp(self):
        a = _make_actor(hp=10)
        a.fighter.take_damage(4)
        assert a.fighter.hp == 6

    def test_take_damage_clamps_to_zero(self):
        a = _make_actor(hp=10)
        dead = a.fighter.take_damage(100)
        assert a.fighter.hp == 0
        assert dead is True

    def test_is_dead_after_lethal_damage(self):
        a = _make_actor(hp=5)
        a.fighter.take_damage(5)
        assert a.fighter.is_dead is True
        assert a.is_alive is False

    def test_is_alive_when_hp_positive(self):
        a = _make_actor(hp=5)
        a.fighter.take_damage(4)
        assert a.fighter.is_dead is False
        assert a.is_alive is True

    def test_attack_deals_damage_to_target(self):
        attacker = _make_actor(hp=10, power=4)
        target = _make_actor(hp=10, power=1)
        damage = attacker.fighter.attack(target)
        assert damage == 4
        assert target.fighter.hp == 6

    def test_attack_can_kill_target(self):
        attacker = _make_actor(hp=10, power=20)
        target = _make_actor(hp=5)
        attacker.fighter.attack(target)
        assert target.fighter.is_dead is True
