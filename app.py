"""
app.py
------
App — central controller of the entire application.
"""

from __future__ import annotations
import os
import sys
import customtkinter as ctk

# Ensure all project modules are importable from any working directory.
#_HERE = os.path.dirname(os.path.abspath(__file__))
#if _HERE not in sys.path:
#    sys.path.insert(0, _HERE)

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "core"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "storage"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "ai"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "gui"))

import jm
from storage.json_manager import JSONManager
from minimax_ai   import MinimaxAI

from main_menu_frame       import MainMenuFrame
from select_id_frame       import SelectIDFrame
from select_symbol_frame   import SelectSymbolFrame
from game_background_frame import GameBackgroundFrame
from leaderboard_frame     import LeaderboardFrame
from exit_frame            import ExitFrame

COMPUTER_ID = "Nash's heir"
_DATA_FILE  = os.path.join(os.path.dirname(__file__), "records.json")


class App:
    _WIDTH  = 420
    _HEIGHT = 540

    def __init__(self) -> None:
        # ── Initialise storage + AI, wire up the jm shim ─────────────── #
        manager = JSONManager(_DATA_FILE)
        ai      = MinimaxAI()
        jm.init(manager, ai)

        # Ensure the computer player has a record entry.
        manager.create_player(COMPUTER_ID)

        # ── Root window ───────────────────────────────────────────────── #
        self.root = ctk.CTk()
        self.root.title("Tic-Tac-Toe")
        self.root.geometry(f"{self._WIDTH}x{self._HEIGHT}")
        self.root.resizable(False, False)

        # ── Shared state ──────────────────────────────────────────────── #
        self.mode:      str  = ""
        self.p1_id:     str  = ""
        self.p2_id:     str  = ""
        self.p1_symbol: str  = ""
        self.p2_symbol: str  = ""
        self.game            = None

        # ── Frame tracking ────────────────────────────────────────────── #
        self._select_id_frame = None
        self._current_frame   = None

        # ── Create long-lived frames once ─────────────────────────────── #
        self.main_menu_frame       = MainMenuFrame(self.root, self)
        self.select_symbol_frame   = SelectSymbolFrame(self.root, self)
        self.game_background_frame = GameBackgroundFrame(self.root, self)
        self.leaderboard_frame     = LeaderboardFrame(self.root, self)
        self.exit_frame            = ExitFrame(self.root, self)

        # ── Start on the main menu ────────────────────────────────────── #
        self._show_frame(self.main_menu_frame)

    # ── Internal frame switcher ──────────────────────────────────────── #

    def _show_frame(self, frame) -> None:
        if self._current_frame is not None:
            self._current_frame.pack_forget()
        frame.pack(fill="both", expand=True)
        self._current_frame = frame

    # ── Navigation ────────────────────────────────────────────────────── #

    def show_main_menu(self) -> None:
        self._show_frame(self.main_menu_frame)

    def show_select_id_p1(self) -> None:
        self._replace_select_id_frame("Player 1", self._on_p1_confirmed)

    def show_select_id_p2(self) -> None:
        self._replace_select_id_frame("Player 2", self._on_p2_confirmed)

    def show_select_id_player(self) -> None:
        self._replace_select_id_frame("Player", self._on_player_confirmed)

    def _replace_select_id_frame(self, label: str, on_confirm) -> None:
        if self._select_id_frame is not None:
            self._select_id_frame.destroy()
            self._select_id_frame = None
        self._select_id_frame = SelectIDFrame(
            self.root, self, label=label, on_confirm=on_confirm
        )
        self._show_frame(self._select_id_frame)

    def show_select_symbol(self) -> None:
        self._show_frame(self.select_symbol_frame)

    def show_game(self) -> None:
        """Build Player + Game objects, store them, show GameBackgroundFrame."""
        p1, p2    = jm.build_players(
            self.p1_id, self.p2_id,
            self.p1_symbol, self.p2_symbol,
            self.mode,
        )
        self.game = jm.build_game(p1, p2)
        self._show_frame(self.game_background_frame)
        self.game_background_frame.on_show()

    def show_leaderboard(self) -> None:
        self._show_frame(self.leaderboard_frame)
        self.leaderboard_frame.on_show()

    def show_exit(self) -> None:
        self._show_frame(self.exit_frame)
        self.exit_frame.on_show()

    # ── Internal callbacks ────────────────────────────────────────────── #

    def _on_p1_confirmed(self, player_id: str) -> None:
        self.p1_id = player_id
        self.show_select_id_p2()

    def _on_p2_confirmed(self, player_id: str) -> None:
        self.p2_id = player_id
        self.show_select_symbol()

    def _on_player_confirmed(self, player_id: str) -> None:
        self.p1_id = player_id
        self.p2_id = COMPUTER_ID
        self.show_select_symbol()