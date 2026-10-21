from pathlib import Path

from PySide6.QtCore import QPoint, QSize, Qt

from pet_app.config import PetSettings, SettingsStore
from pet_app.main_window import PetWindow
from pet_app.states import PetState


def test_pet_window_loads_gif_and_restores_temporary_state(qtbot, tmp_path: Path):
    store = SettingsStore(tmp_path / "settings.json")
    window = PetWindow(PetSettings(), store)
    qtbot.addWidget(window)
    window.resize(QSize(160, 160))
    window.set_state(PetState.ANGRY, temporary_ms=20)
    assert window.settings.current_state == PetState.ANGRY
    qtbot.wait(50)
    assert window.settings.current_state == PetState.IDLE


def test_drag_enters_fearful_and_release_returns_to_idle(qtbot, tmp_path: Path):
    store = SettingsStore(tmp_path / "settings.json")
    window = PetWindow(PetSettings(), store)
    qtbot.addWidget(window)
    qtbot.mousePress(window, Qt.MouseButton.LeftButton, pos=QPoint(20, 20))
    qtbot.mouseMove(window, QPoint(40, 40))
    assert window.settings.current_state == PetState.FEARFUL
    qtbot.mouseRelease(window, Qt.MouseButton.LeftButton, pos=QPoint(40, 40))
    assert window.settings.current_state == PetState.IDLE


def test_repeated_hit_restarts_action(qtbot, tmp_path: Path):
    store = SettingsStore(tmp_path / "settings.json")
    window = PetWindow(PetSettings(), store)
    qtbot.addWidget(window)
    window.set_state(PetState.HIT, temporary_ms=1000)
    movie = window._movie
    window.set_state(PetState.HIT, temporary_ms=1000, force_restart=True)
    assert window.settings.current_state == PetState.HIT
    assert window._movie is not movie
