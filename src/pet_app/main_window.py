from __future__ import annotations

import logging
import time
from pathlib import Path

from PySide6.QtCore import QPoint, Qt, QTimer, Signal
from PySide6.QtGui import QCloseEvent, QIcon, QMovie, QPixmap
from PySide6.QtWidgets import QApplication, QLabel, QMenu, QSystemTrayIcon, QWidget

from .assets import asset_path, find_asset_root
from .behavior import WalkBounds, automatic_state, next_x
from .config import PetSettings, SettingsStore
from .states import TEMPORARY_STATES, PetState, fallback_state

LOGGER = logging.getLogger(__name__)


class PetWindow(QWidget):
    state_changed = Signal(PetState)

    def __init__(self, settings: PetSettings, store: SettingsStore, asset_root: Path | None = None):
        super().__init__()
        self.settings = settings
        self.store = store
        self.asset_root = asset_root
        self._movie: QMovie | None = None
        self._drag_offset: QPoint | None = None
        self._press_position: QPoint | None = None
        self._did_drag = False
        self._click_times: list[float] = []
        self._was_walking = settings.current_state == PetState.WALKING
        self._state_started_at = time.monotonic()
        self._last_interaction_at = time.monotonic()
        self._direction = 1
        self._step = 2
        self._action_timer = QTimer(self)
        self._action_timer.setSingleShot(True)
        self._action_timer.timeout.connect(self._finish_temporary_action)
        self._behavior_timer = QTimer(self)
        self._behavior_timer.timeout.connect(self._tick_behavior)
        self._behavior_timer.start(120)
        self._sleep_timer = QTimer(self)
        self._sleep_timer.timeout.connect(self._tick_sleep)
        self._sleep_timer.start(1_000)
        self._build_window()
        self.set_state(settings.current_state)

    def _build_window(self) -> None:
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.Tool
            | Qt.WindowType.WindowStaysOnTopHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose, True)
        self.setWindowOpacity(self.settings.opacity)
        self.resize(self.settings.width, self.settings.height)
        self.move(self.settings.x, self.settings.y)
        self._label = QLabel(self)
        self._label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        self._label.setGeometry(self.rect())

    def resizeEvent(self, event) -> None:
        if hasattr(self, "_label"):
            self._label.setGeometry(self.rect())
        super().resizeEvent(event)

    def set_state(self, state: PetState, temporary_ms: int | None = None) -> None:
        if state == self.settings.current_state and self._movie is not None:
            return
        self._stop_movie()
        self.settings.current_state = state
        self._state_started_at = time.monotonic()
        self._movie = QMovie(str(asset_path(state, self.asset_root)))
        if not self._movie.isValid():
            LOGGER.warning("动作素材不可用: %s", asset_path(state, self.asset_root))
            self._movie.deleteLater()
            self._movie = QMovie(str(asset_path(PetState.IDLE, self.asset_root)))
            self.settings.current_state = PetState.IDLE
        self._movie.setScaledSize(self.size())
        self._movie.frameChanged.connect(self._on_frame_changed)
        self._movie.start()
        self.state_changed.emit(state)
        if temporary_ms is not None:
            self._action_timer.start(temporary_ms)

    def _on_frame_changed(self) -> None:
        if self._movie:
            self._label.setPixmap(self._movie.currentPixmap())

    def _stop_movie(self) -> None:
        if self._movie:
            self._movie.stop()
            self._movie.deleteLater()
            self._movie = None

    def _finish_temporary_action(self) -> None:
        self.set_state(fallback_state(self.settings.auto_behavior_paused, self._was_walking))

    def _tick_behavior(self) -> None:
        if self.settings.auto_behavior_paused or self.settings.current_state != PetState.WALKING:
            return
        screen = QApplication.primaryScreen()
        if screen is None:
            return
        area = screen.availableGeometry()
        bounds = WalkBounds(area.left(), area.right() - self.width(), area.bottom() - self.height())
        x, self._step = next_x(self.x(), self._direction * abs(self._step), bounds)
        self._direction = 1 if self._step >= 0 else -1
        self.move(x, bounds.y)

    def _tick_sleep(self) -> None:
        idle_seconds = time.monotonic() - self._last_interaction_at
        new_state = automatic_state(
            self.settings.current_state,
            self.settings.auto_behavior_paused,
            idle_seconds,
            300,
            walk_after_seconds=5,
        )
        if new_state != self.settings.current_state:
            self.set_state(new_state)

    def mousePressEvent(self, event) -> None:
        self._last_interaction_at = time.monotonic()
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_offset = event.position().toPoint()
            self._press_position = event.position().toPoint()
            self._did_drag = False
            self._was_walking = self.settings.current_state == PetState.WALKING
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event) -> None:
        if self._drag_offset is not None and event.buttons() & Qt.MouseButton.LeftButton:
            if self._press_position is not None and (
                event.position().toPoint() - self._press_position
            ).manhattanLength() > 6:
                self._did_drag = True
            self.move(event.globalPosition().toPoint() - self._drag_offset)
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event) -> None:
        if event.button() == Qt.MouseButton.LeftButton and not self._did_drag:
            self._handle_click(event)
        self._drag_offset = None
        self._press_position = None
        super().mouseReleaseEvent(event)

    def _handle_click(self, event) -> None:
        now = time.monotonic()
        if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            self._click_times.clear()
            self.set_state(PetState.ANGRY, temporary_ms=1_500)
            return
        self._click_times = [stamp for stamp in self._click_times if now - stamp <= 0.8]
        self._click_times.append(now)
        if len(self._click_times) >= 3:
            self._click_times.clear()
            self.set_state(PetState.HIT, temporary_ms=1_200)
        else:
            self.set_state(PetState.RELAXED, temporary_ms=1_500)

    def contextMenuEvent(self, event) -> None:
        menu = QMenu(self)
        self._populate_menu(menu)
        menu.exec(event.globalPos())

    def _populate_menu(self, menu: QMenu) -> None:
        behavior_action = menu.addAction("恢复自动行为" if self.settings.auto_behavior_paused else "暂停自动行为")
        behavior_action.triggered.connect(self.toggle_auto_behavior)
        menu.addSeparator()
        for state, title in (
            (PetState.IDLE, "待机"),
            (PetState.WALKING, "行走"),
            (PetState.RELAXED, "放松"),
            (PetState.ALERT, "警觉"),
            (PetState.HIT, "受击"),
            (PetState.SLEEPING, "睡觉"),
            (PetState.ANGRY, "生气"),
        ):
            action = menu.addAction(title)
            action.triggered.connect(lambda _checked=False, value=state: self.set_state(value))
        menu.addSeparator()
        topmost_action = menu.addAction("取消置顶" if self.settings.topmost else "置顶")
        topmost_action.triggered.connect(self.toggle_topmost)
        hide_action = menu.addAction("隐藏桌宠")
        hide_action.triggered.connect(self.hide)
        save_action = menu.addAction("保存当前设置")
        save_action.triggered.connect(self.save_settings)
        menu.addSeparator()
        exit_action = menu.addAction("退出程序")
        exit_action.triggered.connect(QApplication.instance().quit)

    def toggle_auto_behavior(self) -> None:
        self.settings.auto_behavior_paused = not self.settings.auto_behavior_paused
        if self.settings.auto_behavior_paused and self.settings.current_state == PetState.WALKING:
            self.set_state(PetState.IDLE)

    def toggle_topmost(self) -> None:
        self.settings.topmost = not self.settings.topmost
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, self.settings.topmost)
        self.show()

    def save_settings(self) -> None:
        self.settings.x, self.settings.y = self.x(), self.y()
        self.settings.width, self.settings.height = self.width(), self.height()
        self.settings.opacity = self.windowOpacity()
        self.store.save(self.settings)

    def closeEvent(self, event: QCloseEvent) -> None:
        self.save_settings()
        self._stop_movie()
        event.accept()


class PetTray:
    def __init__(self, window: PetWindow):
        self.window = window
        self.tray = QSystemTrayIcon(window)
        icon_root = window.asset_root or find_asset_root()
        self.tray.setIcon(QIcon(QPixmap(str(icon_root / "正面图.png"))))
        self.tray.setToolTip("月牙雪熊")
        menu = QMenu()
        show_action = menu.addAction("显示桌宠")
        show_action.triggered.connect(self.show_window)
        menu.addAction("退出程序", QApplication.instance().quit)
        self.tray.setContextMenu(menu)
        self.tray.activated.connect(self._activated)
        self.tray.show()

    def _activated(self, reason: QSystemTrayIcon.ActivationReason) -> None:
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            self.show_window()

    def show_window(self) -> None:
        self.window.show()
        self.window.raise_()
        self.window.activateWindow()
