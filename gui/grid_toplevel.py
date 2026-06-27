"""
grid_toplevel.py
----------------
GridTopLevel — the 3×3 clickable game board shown as a Tk Toplevel.
"""

from __future__ import annotations

import tkinter as tk
import customtkinter as ctk

import jm
from result_modal import ResultModal

_SYMBOL_COLOURS: dict[str, str] = {"X": "red", "O": "blue"}


def _default_fg() -> str:
    mode_idx = 0 if ctk.get_appearance_mode() == "Light" else 1
    try:
        return ctk.ThemeManager.theme["CTkLabel"]["text_color"][mode_idx]
    except (KeyError, IndexError):
        return "black"


class GridTopLevel(tk.Toplevel):
    """3 × 3 game-board window."""

    _BTN_FONT    = ("Courier", 48, "bold")
    _AI_DELAY_MS = 150

    def __init__(self, master, app, on_game_over) -> None:
        super().__init__(master)
        self._app          = app
        self._on_game_over = on_game_over
        self._owner        = master          # GameBackgroundFrame
        self._buttons: dict[tuple[int, int], tk.Button] = {}

        self.title("Tic-Tac-Toe")
        self.resizable(False, False)
        self.attributes("-topmost", True)

        self._build_grid()

    # ── UI ───────────────────────────────────────────────────────────── #

    def _build_grid(self) -> None:
        for r in range(3):
            for c in range(3):
                btn = tk.Button(
                    self,
                    text="",
                    font=self._BTN_FONT,
                    width=3,
                    height=1,
                    relief="ridge",
                    command=lambda row=r, col=c: self.on_cell_click(row, col),
                )
                btn.grid(row=r, column=c, padx=4, pady=4, ipadx=18, ipady=18)
                self._buttons[(r, c)] = btn

    # ── Public ───────────────────────────────────────────────────────── #

    def on_cell_click(self, r: int, c: int) -> None:
        game = self._app.game
        # Capture the current player BEFORE make_move (which switches turns).
        acting_player = game.current_player
        if not game.make_move(r, c):
            return
        self._mark_cell(r, c, acting_player.symbol)
        self._check_end_or_continue(acting_player)

    def do_ai_turn(self) -> None:
        game = self._app.game
        acting_player = game.current_player
        move = jm.get_ai_move(game.board, acting_player.symbol)
        if move is None:
            return
        r, c = move
        if not game.make_move(r, c):
            return
        self._mark_cell(r, c, acting_player.symbol)
        self._check_end_or_continue(acting_player)

    def reset(self) -> None:
        default_fg = _default_fg()
        for btn in self._buttons.values():
            btn.configure(text="", fg=default_fg, state=tk.NORMAL)

    # ── Private ──────────────────────────────────────────────────────── #

    def _mark_cell(self, r: int, c: int, symbol: str) -> None:
        colour = _SYMBOL_COLOURS.get(symbol, "black")
        self._buttons[(r, c)].configure(text=symbol, fg=colour, state=tk.DISABLED)

    def _lock_empty_cells(self) -> None:
        for btn in self._buttons.values():
            if btn.cget("text") == "":
                btn.configure(state=tk.DISABLED)

    def _check_end_or_continue(self, last_player) -> None:
        """Use game.check_game_state() — the real Game API."""
        game  = self._app.game
        state = game.check_game_state()

        if state == "win":
            self._lock_empty_cells()
            self._show_result_modal(winner=last_player)
            return

        if state == "draw":
            self._lock_empty_cells()
            self._show_result_modal(winner=None)
            return

        # Game continues — schedule AI if it is the next player's turn.
        if getattr(game.current_player, "is_computer", False):
            self.after(self._AI_DELAY_MS, self._owner._do_ai_turn)

    def _show_result_modal(self, winner) -> None:
        if winner is not None:
            result_key = (
                "p1_win"
                if winner.player_id == self._app.p1_id
                else "p2_win"
            )
        else:
            result_key = "draw"

        ResultModal(
            master=self,
            app=self._app,
            result=result_key,
            on_dismiss=self._on_game_over,
        )