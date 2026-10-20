from pathlib import Path

from PySide6.QtCore import QSize

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
