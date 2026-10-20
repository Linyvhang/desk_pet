from __future__ import annotations

from dataclasses import dataclass

from .states import PetState


@dataclass(frozen=True)
class WalkBounds:
    left: int
    right: int
    y: int


def next_x(x: int, step: int, bounds: WalkBounds) -> tuple[int, int]:
    """Move horizontally and reverse direction at the configured boundary."""
    if bounds.right <= bounds.left:
        return bounds.left, -1
    candidate = x + step
    if candidate >= bounds.right:
        return bounds.right, -abs(step)
    if candidate <= bounds.left:
        return bounds.left, abs(step)
    return candidate, step


def should_sleep(idle_seconds: float, threshold_seconds: float) -> bool:
    return idle_seconds >= threshold_seconds


def automatic_state(
    current: PetState,
    paused: bool,
    idle_seconds: float,
    sleep_after_seconds: float,
    walk_after_seconds: float = 5.0,
) -> PetState:
    if paused or current not in {PetState.IDLE, PetState.WALKING, PetState.SLEEPING}:
        return current
    if should_sleep(idle_seconds, sleep_after_seconds):
        return PetState.SLEEPING
    if current == PetState.IDLE and idle_seconds >= walk_after_seconds:
        return PetState.WALKING
    return current
