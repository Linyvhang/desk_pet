from __future__ import annotations

import logging
import os
import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication

from .assets import validate_assets
from .config import SettingsStore
from .main_window import PetTray, PetWindow


def settings_path() -> Path:
    app_data = os.environ.get("APPDATA")
    root = Path(app_data) if app_data else Path.home() / "AppData" / "Roaming"
    return root / "YueyaSnowBear" / "settings.json"


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    missing = validate_assets()
    if missing:
        logging.warning("缺少动作素材: %s", ", ".join(map(str, missing)))
    app = QApplication(sys.argv)
    app.setApplicationName("月牙雪熊")
    app.setQuitOnLastWindowClosed(False)
    store = SettingsStore(settings_path())
    window = PetWindow(store.load(), store)
    tray = PetTray(window)
    window.show()
    app.aboutToQuit.connect(window.save_settings)
    app.aboutToQuit.connect(tray.tray.hide)
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
