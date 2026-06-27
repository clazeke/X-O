"""
result_modal.py
---------------
ResultModal — end-of-match popup shown over the game board.
"""

from __future__ import annotations

import tkinter as tk
import customtkinter as ctk

import jm


class ResultModal(tk.Toplevel):
    _RESULT_FONT = ("Courier", 18, "bold")
    _BTN_FONT    = ("Courier", 13, "bold")

    def __init__(self, master, app, result: str, on_dismiss) -> None:
        super().__init__(master)
        self._app        = app
        self._result     = result
        self._on_dismiss = on_dismiss

        self.title("Result")
        self.resizable(False, False)
        self.attributes("-topmost", True)
        self.protocol("WM_DELETE_WINDOW", lambda: None)

        self._build_ui()
        self._write_records()

        self.update_idletasks()
        self._centre_on_master(master)

    def _build_ui(self) -> None:
        container = tk.Frame(self, padx=30, pady=24)
        container.pack()

        tk.Label(
            container,
            text=self._result_text(),
            font=self._RESULT_FONT,
            wraplength=320,
            justify="center",
        ).pack(pady=(0, 20))

        btn_frame = tk.Frame(container)
        btn_frame.pack()

        tk.Button(
            btn_frame, text="Rematch",
            font=self._BTN_FONT, width=12, height=2,
            command=self._on_rematch,
        ).grid(row=0, column=0, padx=10)

        tk.Button(
            btn_frame, text="Main Menu",
            font=self._BTN_FONT, width=12, height=2,
            command=self._on_main_menu,
        ).grid(row=0, column=1, padx=10)

    def _result_text(self) -> str:
        if self._result == "draw":
            return "Stalemate"
        if self._result == "p1_win":
            return f"{self._app.p1_id} wins! {self._app.p2_id} loses."
        return f"{self._app.p2_id} wins! {self._app.p1_id} loses."

    def _write_records(self) -> None:
        """Persist result — JSONManager.update_record needs (id, symbol, result)."""
        game = self._app.game
        p1   = game.player_1
        p2   = game.player_2

        if self._result == "draw":
            jm.update_record(p1.player_id, p1.symbol, "draw")
            jm.update_record(p2.player_id, p2.symbol, "draw")
        elif self._result == "p1_win":
            jm.update_record(p1.player_id, p1.symbol, "win")
            jm.update_record(p2.player_id, p2.symbol, "loss")
        else:
            jm.update_record(p1.player_id, p1.symbol, "loss")
            jm.update_record(p2.player_id, p2.symbol, "win")

    def _centre_on_master(self, master) -> None:
        try:
            mx = master.winfo_rootx() + master.winfo_width()  // 2
            my = master.winfo_rooty() + master.winfo_height() // 2
            w  = self.winfo_width()
            h  = self.winfo_height()
            self.geometry(f"+{mx - w // 2}+{my - h // 2}")
        except tk.TclError:
            pass

    def _dismiss(self, result_key: str) -> None:
        self.destroy()
        self._on_dismiss(result_key)

    def _on_rematch(self)   -> None: self._dismiss(self._result)
    def _on_main_menu(self) -> None: self._dismiss("main_menu")