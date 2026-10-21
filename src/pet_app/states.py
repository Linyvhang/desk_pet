from __future__ import annotations

from enum import Enum


class PetState(str, Enum):
    IDLE = "idle"
    WALKING = "walking"
    RELAXED = "relaxed"
    ALERT = "alert"
    FEARFUL = "fearful"
    HIT = "hit"
    SLEEPING = "sleeping"
    ANGRY = "angry"


TEMPORARY_STATES = frozenset(
    {
        PetState.RELAXED,
        PetState.ALERT,
        PetState.FEARFUL,
        PetState.HIT,
        PetState.ANGRY,
    }
)


STATE_ASSETS: dict[PetState, str] = {
    PetState.IDLE: "待机.gif",
    PetState.WALKING: "行走.gif",
    PetState.RELAXED: "放松.gif",
    PetState.ALERT: "警觉.gif",
    PetState.FEARFUL: "害怕.gif",
    PetState.HIT: "受击.gif",
    PetState.SLEEPING: "睡觉.gif",
    PetState.ANGRY: "生气.gif",
}


def parse_state(value: str | PetState | None) -> PetState:
    """Convert persisted input to a safe state, falling back to idle."""
    if isinstance(value, PetState):
        return value
    try:
        return PetState(value or PetState.IDLE.value)
    except ValueError:
        return PetState.IDLE


def fallback_state(auto_behavior_paused: bool, was_walking: bool = False) -> PetState:
    """Return the idle state after any temporary action finishes."""
    return PetState.IDLE
