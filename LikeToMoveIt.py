"""Simple Tkinter timer that moves the mouse randomly while running.

Requires: pip install pyautogui
"""

import importlib.util
import random
import threading
import time
import tkinter as tk
from tkinter import messagebox, ttk

pyautogui = None  # lazy-loaded to avoid import-time display errors
pyautogui_error: str | None = None
PYAUTOGUI_INSTALLED = importlib.util.find_spec("pyautogui") is not None


class MouseMoverApp:
    def __init__(self) -> None:
        self.root = tk.Tk()
        self.root.title("LikeToMoveIt")
        self.root.resizable(False, False)

        self.duration_var = tk.StringVar(value="10")  # minutes
        self.status_var = tk.StringVar(value="Pret")
        self.countdown_var = tk.StringVar(value="00:00")

        self.stop_event = threading.Event()
        self.end_time: float | None = None
        self.running = False

        self._build_ui()
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

    def _build_ui(self) -> None:
        main = ttk.Frame(self.root, padding=12)
        main.grid(row=0, column=0, sticky="nsew")

        ttk.Label(main, text="Duree (minutes)").grid(row=0, column=0, sticky="w")
        ttk.Entry(main, width=10, textvariable=self.duration_var).grid(
            row=0, column=1, sticky="w", padx=(6, 0)
        )

        btn_frame = ttk.Frame(main)
        btn_frame.grid(row=1, column=0, columnspan=2, pady=(10, 4), sticky="ew")
        self.start_button = ttk.Button(btn_frame, text="Demarrer", command=self.start_timer)
        self.start_button.grid(row=0, column=0, padx=(0, 6))
        self.stop_button = ttk.Button(
            btn_frame, text="Arret", command=self.stop_timer, state=tk.DISABLED
        )
        self.stop_button.grid(row=0, column=1)

        ttk.Label(main, text="Temps restant").grid(row=2, column=0, sticky="w", pady=(10, 0))
        ttk.Label(main, textvariable=self.countdown_var, font=("TkDefaultFont", 16)).grid(
            row=2, column=1, sticky="w", pady=(10, 0)
        )

        ttk.Label(main, text="Statut").grid(row=3, column=0, sticky="w", pady=(6, 0))
        ttk.Label(main, textvariable=self.status_var).grid(row=3, column=1, sticky="w", pady=(6, 0))

        for i in range(2):
            main.columnconfigure(i, weight=1)

        if not PYAUTOGUI_INSTALLED:
            self.status_var.set("Installez pyautogui (pip install pyautogui)")

    def start_timer(self) -> None:
        if self.running:
            return
        if not self._ensure_pyautogui():
            return
        try:
            minutes = float(self.duration_var.get())
        except ValueError:
            messagebox.showerror("Valeur invalide", "Entrez un nombre de minutes.")
            return
        if minutes <= 0:
            messagebox.showerror("Valeur invalide", "La duree doit etre positive.")
            return

        self.end_time = time.time() + minutes * 60
        self.stop_event.clear()
        self.running = True
        self.start_button.state(["disabled"])
        self.stop_button.state(["!disabled"])
        self.status_var.set("En cours...")
        self._update_countdown()

        thread = threading.Thread(target=self._mouse_loop, daemon=True)
        thread.start()

    def stop_timer(self) -> None:
        self.stop_event.set()
        self._finish("Arrete")

    def _finish(self, status: str) -> None:
        self.running = False
        self.start_button.state(["!disabled"])
        self.stop_button.state(["disabled"])
        self.status_var.set(status)
        self.countdown_var.set("00:00")

    def _update_countdown(self) -> None:
        if not self.running or self.end_time is None:
            return
        remaining = max(0, int(self.end_time - time.time()))
        minutes, seconds = divmod(remaining, 60)
        self.countdown_var.set(f"{minutes:02d}:{seconds:02d}")
        if remaining <= 0 or self.stop_event.is_set():
            self._finish("Termine")
            return
        self.root.after(200, self._update_countdown)

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
            self.root.after(0, lambda: self._finish("Interrompu (coin ecran)"))
            return
        self.root.after(0, lambda: self._finish("Termine"))

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
        messagebox.showerror("PyAutoGUI indisponible", msg)
        self.status_var.set("Erreur pyautogui")
        return False

    def _on_close(self) -> None:
        self.stop_event.set()
        self.root.destroy()

    def run(self) -> None:
        self.root.mainloop()


if __name__ == "__main__":
    app = MouseMoverApp()
    app.run()
