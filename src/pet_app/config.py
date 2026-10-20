from __future__ import annotations

import json
import logging
import os
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from .states import PetState, parse_state

LOGGER = logging.getLogger(__name__)


@dataclass
class PetSettings:
    x: int = 100
    y: int = 100
    width: int = 180
    height: int = 180
    opacity: float = 1.0
    topmost: bool = True
    auto_behavior_paused: bool = False
    current_state: PetState = PetState.IDLE

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "PetSettings":
        position = data.get("position") or {}
        size = data.get("size") or {}
        return cls(
            x=_as_int(position.get("x"), cls.x),
            y=_as_int(position.get("y"), cls.y),
            width=max(32, _as_int(size.get("width"), cls.width)),
            height=max(32, _as_int(size.get("height"), cls.height)),
            opacity=min(1.0, max(0.1, _as_float(data.get("opacity"), cls.opacity))),
            topmost=_as_bool(data.get("topmost"), cls.topmost),
            auto_behavior_paused=_as_bool(
                data.get("auto_behavior_paused"), cls.auto_behavior_paused
            ),
            current_state=parse_state(data.get("current_state")),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "position": {"x": self.x, "y": self.y},
            "size": {"width": self.width, "height": self.height},
            "opacity": self.opacity,
            "topmost": self.topmost,
            "auto_behavior_paused": self.auto_behavior_paused,
            "current_state": self.current_state.value,
        }


@dataclass
class SettingsStore:
    path: Path
    defaults: PetSettings = field(default_factory=PetSettings)

    def load(self) -> PetSettings:
        try:
            with self.path.open("r", encoding="utf-8") as stream:
                payload = json.load(stream)
            if not isinstance(payload, dict):
                raise ValueError("settings root must be an object")
            return PetSettings.from_dict(payload)
        except FileNotFoundError:
            return self.defaults
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            LOGGER.warning("无法读取设置 %s: %s", self.path, exc)
            return self.defaults

    def save(self, settings: PetSettings) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        fd, temporary_name = tempfile.mkstemp(
            prefix=f"{self.path.stem}.", suffix=".tmp", dir=self.path.parent
        )
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as stream:
                json.dump(settings.to_dict(), stream, ensure_ascii=False, indent=2)
                stream.write("\n")
            os.replace(temporary_name, self.path)
        except Exception:
            try:
                os.unlink(temporary_name)
            except OSError:
                pass
            raise


def _as_int(value: Any, default: int) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _as_float(value: Any, default: float) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _as_bool(value: Any, default: bool) -> bool:
    return value if isinstance(value, bool) else default
