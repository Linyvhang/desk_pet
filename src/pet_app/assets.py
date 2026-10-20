from __future__ import annotations

from pathlib import Path

from .states import STATE_ASSETS, PetState


def find_asset_root() -> Path:
    """Resolve assets in both source checkout and PyInstaller bundles."""
    import sys

    bundled_root = getattr(sys, "_MEIPASS", None)
    if bundled_root:
        candidate = Path(bundled_root) / "月牙雪熊"
        if candidate.exists():
            return candidate
    return Path(__file__).resolve().parents[2] / "月牙雪熊"


def asset_path(state: PetState, root: Path | None = None) -> Path:
    return (root or find_asset_root()) / STATE_ASSETS[state]


def validate_assets(root: Path | None = None) -> list[Path]:
    root = root or find_asset_root()
    return [asset_path(state, root) for state in STATE_ASSETS if not asset_path(state, root).is_file()]
