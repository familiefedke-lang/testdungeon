"""
Game – owns the pygame event loop and frame timing.

Responsibilities
- processes pygame events via InputHandler
- computes dt (seconds since last frame)
- calls engine.update(dt)  (animations – every frame)
- calls engine.try_player_command(cmd) + engine.enemy_turns() on player input
- calls engine.render(renderer)
- flips the display
"""

from __future__ import annotations

import pygame

from src.constants import FPS
from src.engine import Engine
from src.input.input_handler import InputHandler
from src.render.renderer import Renderer


class Game:
    def __init__(self, engine: Engine, renderer: Renderer) -> None:
        self.engine = engine
        self.renderer = renderer
        self.input_handler = InputHandler()
        self._clock = pygame.time.Clock()

    def run(self) -> None:
        self.engine.new_game()

        while self.engine.running:
            dt = self._clock.tick(FPS) / 1000.0  # seconds

            # --- Input ---
            for event in pygame.event.get():
                cmd = self.input_handler.handle_event(event)
                if cmd is not None:
                    turn_taken = self.engine.try_player_command(cmd)
                    if turn_taken:
                        self.engine.enemy_turns()

            # --- Update (animations) ---
            self.engine.update(dt)

            # --- Render ---
            self.engine.render(self.renderer)
            self.renderer.present()
