"""
Input command objects and input handler.

The handler maps pygame events/key-state to command objects.
Returning None means "no action this frame".
"""

from __future__ import annotations

from dataclasses import dataclass

import pygame


# ---------------------------------------------------------------------------
# Command types
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Move:
    dx: int
    dy: int


@dataclass(frozen=True)
class UseStairs:
    pass


@dataclass(frozen=True)
class Pickup:
    """Pick up an item on the current tile."""
    pass


@dataclass(frozen=True)
class Quit:
    pass


Command = Move | UseStairs | Pickup | Quit


# ---------------------------------------------------------------------------
# Key → command mapping
# ---------------------------------------------------------------------------

_KEY_TO_MOVE: dict[int, tuple[int, int]] = {
    # Arrow keys
    pygame.K_UP:    (0, -1),
    pygame.K_DOWN:  (0,  1),
    pygame.K_LEFT:  (-1, 0),
    pygame.K_RIGHT: (1,  0),
    # Vi-keys
    pygame.K_k: (0, -1),
    pygame.K_j: (0,  1),
    pygame.K_h: (-1, 0),
    pygame.K_l: (1,  0),
    # Numpad
    pygame.K_KP8: (0, -1),
    pygame.K_KP2: (0,  1),
    pygame.K_KP4: (-1, 0),
    pygame.K_KP6: (1,  0),
    # Diagonal (numpad)
    pygame.K_KP7: (-1, -1),
    pygame.K_KP9: (1, -1),
    pygame.K_KP1: (-1, 1),
    pygame.K_KP3: (1,  1),
}


class InputHandler:
    """Converts a pygame event into a Command (or None)."""

    def handle_event(self, event: pygame.event.Event) -> "Command | None":
        if event.type == pygame.QUIT:
            return Quit()

        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_ESCAPE, pygame.K_q):
                return Quit()

            if event.key in (pygame.K_PERIOD, pygame.K_KP5):
                # > or numpad-5 → use stairs / wait
                return UseStairs()

            if event.key == pygame.K_e:
                # pick up item
                return Pickup()

            if event.key in _KEY_TO_MOVE:
                dx, dy = _KEY_TO_MOVE[event.key]
                return Move(dx, dy)

        return None