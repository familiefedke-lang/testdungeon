"""
SpriteComponent – animation state machine for an Actor.

Tracks:
  - current animation name ("idle", "walk", "attack", "hurt", "dead")
  - facing direction ("N", "S", "E", "W")
  - frame index within the animation
  - per-frame timer
  - optional lock (forces an animation to finish before returning to idle)
"""

from __future__ import annotations


class SpriteComponent:
    DEFAULT_FPS: float = 8.0  # animation frames per second

    def __init__(self, sprite_key: str, anim: str = "idle", facing: str = "S") -> None:
        self.sprite_key: str = sprite_key
        self.anim: str = anim
        self.facing: str = facing
        self._frame_index: int = 0
        self._frame_timer: float = 0.0
        self._lock_timer: float = 0.0  # > 0 means animation is locked

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def play(self, anim: str, lock_for: float = 0.0) -> None:
        """Switch to *anim*, optionally locking it for *lock_for* seconds."""
        if self.anim != anim:
            self.anim = anim
            self._frame_index = 0
            self._frame_timer = 0.0
        self._lock_timer = max(self._lock_timer, lock_for)

    def update(self, dt: float, animation_db: "AnimationDB | None" = None) -> None:  # noqa: F821
        """Advance frame timer and lock timer by *dt* seconds."""
        if self._lock_timer > 0.0:
            self._lock_timer -= dt
            if self._lock_timer <= 0.0:
                self._lock_timer = 0.0
                # Return to idle only if not permanently locked (dead)
                if self.anim not in ("dead",):
                    self.anim = "idle"
                    self._frame_index = 0
                    self._frame_timer = 0.0

        # Advance animation frame
        fps = self.DEFAULT_FPS
        if animation_db is not None:
            fps = animation_db.get_fps(self.sprite_key, self.anim)
        frame_duration = 1.0 / fps
        self._frame_timer += dt
        if animation_db is not None:
            frame_count = len(animation_db.get_frames(self.sprite_key, self.anim, self.facing))
        else:
            frame_count = 1
        if frame_count > 0 and self._frame_timer >= frame_duration:
            self._frame_timer -= frame_duration
            self._frame_index = (self._frame_index + 1) % max(frame_count, 1)

    def current_frame_index(self, animation_db: "AnimationDB | None" = None) -> int:  # noqa: F821
        """Return the current atlas tile index for this actor."""
        if animation_db is not None:
            frames = animation_db.get_frames(self.sprite_key, self.anim, self.facing)
            if frames:
                return frames[self._frame_index % len(frames)]
        return 0

    def set_facing_from_delta(self, dx: int, dy: int) -> None:
        if dx > 0:
            self.facing = "E"
        elif dx < 0:
            self.facing = "W"
        elif dy < 0:
            self.facing = "N"
        elif dy > 0:
            self.facing = "S"
