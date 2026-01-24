"""Simple PySide6 timer that moves the mouse randomly while running.

Requires: pip install pyautogui pyside6
"""

from __future__ import annotations

import importlib.util
import random
import sys
import threading
import time

from PySide6 import QtCore, QtWidgets

pyautogui = None  # lazy-loaded to avoid import-time display errors
pyautogui_error: str | None = None
PYAUTOGUI_INSTALLED = importlib.util.find_spec("pyautogui") is not None


class MouseMoverApp(QtWidgets.QWidget):
    finished = QtCore.Signal(str)

    def __init__(self) -> None:
        super().__init__()

        self.setWindowTitle("LikeToMoveIt")
        self.setFixedSize(280, 170)

        self.duration_input = QtWidgets.QLineEdit("10")
        self.duration_input.setFixedWidth(80)

        self.countdown_label = QtWidgets.QLabel("00:00")
        self.countdown_label.setStyleSheet("font-size: 16px;")

        self.status_label = QtWidgets.QLabel("Pret")

        self.start_button = QtWidgets.QPushButton("Demarrer")
        self.stop_button = QtWidgets.QPushButton("Arret")
        self.stop_button.setEnabled(False)

        self.stop_event = threading.Event()
        self.end_time: float | None = None
        self.running = False

        self.countdown_timer = QtCore.QTimer(self)
        self.countdown_timer.setInterval(200)
        self.countdown_timer.timeout.connect(self._update_countdown)

        self.start_button.clicked.connect(self.start_timer)
        self.stop_button.clicked.connect(self.stop_timer)
        self.finished.connect(self._finish)

        self._build_ui()

        if not PYAUTOGUI_INSTALLED:
            self.status_label.setText("Installez pyautogui (pip install pyautogui)")

    def _build_ui(self) -> None:
        layout = QtWidgets.QGridLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setHorizontalSpacing(8)
        layout.setVerticalSpacing(8)

        layout.addWidget(QtWidgets.QLabel("Duree (minutes)"), 0, 0)
        layout.addWidget(self.duration_input, 0, 1)

        button_row = QtWidgets.QHBoxLayout()
        button_row.addWidget(self.start_button)
        button_row.addWidget(self.stop_button)
        button_row.addStretch(1)
        layout.addLayout(button_row, 1, 0, 1, 2)

        layout.addWidget(QtWidgets.QLabel("Temps restant"), 2, 0)
        layout.addWidget(self.countdown_label, 2, 1)

        layout.addWidget(QtWidgets.QLabel("Statut"), 3, 0)
        layout.addWidget(self.status_label, 3, 1)

        layout.setColumnStretch(0, 1)
        layout.setColumnStretch(1, 1)

    def start_timer(self) -> None:
        if self.running:
            return
        if not self._ensure_pyautogui():
            return
        try:
            minutes = float(self.duration_input.text())
        except ValueError:
            QtWidgets.QMessageBox.critical(self, "Valeur invalide", "Entrez un nombre de minutes.")
            return
        if minutes <= 0:
            QtWidgets.QMessageBox.critical(self, "Valeur invalide", "La duree doit etre positive.")
            return

        self.end_time = time.time() + minutes * 60
        self.stop_event.clear()
        self.running = True
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.status_label.setText("En cours...")
        self._update_countdown()
        self.countdown_timer.start()

        thread = threading.Thread(target=self._mouse_loop, daemon=True)
        thread.start()

    def stop_timer(self) -> None:
        self.stop_event.set()
        self._finish("Arrete")

    def _finish(self, status: str) -> None:
        self.running = False
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.status_label.setText(status)
        self.countdown_label.setText("00:00")
        self.countdown_timer.stop()

    def _update_countdown(self) -> None:
        if not self.running or self.end_time is None:
            return
        remaining = max(0, int(self.end_time - time.time()))
        minutes, seconds = divmod(remaining, 60)
        self.countdown_label.setText(f"{minutes:02d}:{seconds:02d}")
        if remaining <= 0 or self.stop_event.is_set():
            self._finish("Termine")

    def _mouse_loop(self) -> None:
        assert pyautogui is not None  # ensured in start_timer
        width, height = pyautogui.size()
        try:
            while not self.stop_event.is_set() and self.end_time and time.time() < self.end_time:
                x, y = pyautogui.position()
                dx = random.randint(-80, 80)
                dy = random.randint(-80, 80)
                new_x = min(max(x + dx, 0), width - 1)
                new_y = min(max(y + dy, 0), height - 1)
                move_duration = random.uniform(0.15, 0.45)
                pyautogui.moveTo(
                    new_x,
                    new_y,
                    duration=move_duration,
                    tween=pyautogui.easeInOutQuad,
                )
                pause = random.uniform(1.0, 3.0)
                if self.stop_event.wait(pause):
                    break
        except pyautogui.FailSafeException:
            self.stop_event.set()
            self.finished.emit("Interrompu (coin ecran)")
            return
        self.finished.emit("Termine")

    def _ensure_pyautogui(self) -> bool:
        """Lazy-load pyautogui and surface helpful errors."""
        global pyautogui, pyautogui_error
        if pyautogui is not None:
            return True
        try:
            import pyautogui as _p  # type: ignore

            pyautogui = _p
            pyautogui.FAILSAFE = True
            return True
        except ImportError:
            msg = "Installez pyautogui : pip install pyautogui"
        except Exception as exc:  # display / X11 issues, etc.
            pyautogui_error = str(exc)
            msg = (
                "Impossible de charger pyautogui.\n"
                f"Erreur: {pyautogui_error}\n\n"
                "Assurez-vous de lancer le programme depuis une session graphique "
                "(DISPLAY/Xauthority) et sans sudo."
            )
        QtWidgets.QMessageBox.critical(self, "PyAutoGUI indisponible", msg)
        self.status_label.setText("Erreur pyautogui")
        return False

    def closeEvent(self, event: QtCore.QEvent) -> None:
        self.stop_event.set()
        event.accept()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MouseMoverApp()
    window.show()
    sys.exit(app.exec())
