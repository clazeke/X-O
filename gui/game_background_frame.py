"""
game_background_frame.py
------------------------
GameBackgroundFrame — the persistent backdrop visible for the entire match
session, including across rematches.

Owns and manages a single GridTopLevel instance.  The toplevel is never
destroyed mid-session; it is cleared and reused on each rematch.  It is
only destroyed when the player chooses "Main Menu" from the result modal.

Dependencies:
    customtkinter
    grid_toplevel.GridTopLevel
    App (passed in as `app`) — must expose:
        app.p1_id        (str)
        app.p2_id        (str)
        app.game         (Game)  — must expose:
            game.start_new_game() → None
            game.current_player   — Player whose turn it is
            game.p1 / game.p2     — Player objects; each has .is_ai (bool)
        app.show_main_menu()     — navigation back to MainMenuFrame

    Game / Player contract expected by this frame:
        game.start_new_game()
        game.current_player.is_ai  →  bool
        (AI turn logic lives in GridTopLevel / jm; this frame only
         schedules the first AI move when the computer goes first)
"""

from __future__ import annotations

import customtkinter as ctk



class GameBackgroundFrame(ctk.CTkFrame):
    """Persistent match-session backdrop.

    Layout (top-to-bottom, centred):
        ┌──────────────────────────────────────────┐
        │  Alice: 2   Draws: 1   Bob: 1            │  ← session stats label
        │                                          │
        │  (GridTopLevel floats above this frame)  │
        └──────────────────────────────────────────┘

    Lifecycle
    ---------
    on_show() must be called by App immediately after packing this frame.
    It initialises session counters and opens the first match.

    Between rematches the GridTopLevel is *reused* (reset, not destroyed).
    It is destroyed only when the player navigates back to the main menu.
    """

    _AI_DELAY_MS = 150   # ms before the first AI move when AI goes first

    def __init__(self, parent, app) -> None:
        super().__init__(parent, fg_color="transparent")
        self._app      = app
        self._toplevel = None  # GridTopLevel instance, created lazily
        self._session: dict = {}

        self._build_ui()

    # ── UI construction ──────────────────────────────────────────────── #

    def _build_ui(self) -> None:
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        # Stats label — text is set dynamically by _refresh_stats_label().
        self._stats_label = ctk.CTkLabel(
            self,
            text="",
            font=ctk.CTkFont(family="Courier", size=15, weight="bold"),
        )
        self._stats_label.grid(row=0, column=0, pady=(18, 0), sticky="n")

    # ── Lifecycle ────────────────────────────────────────────────────── #

    def on_show(self) -> None:
        """Call immediately after the frame is packed/shown by App.

        Initialises per-session counters and kicks off the first match.
        """
        p1 = self._app.p1_id
        p2 = self._app.p2_id
        self._session = {
            p1:      {"wins": 0},
            p2:      {"wins": 0},
            "draws": 0,
        }
        self._refresh_stats_label()
        self.start_match()

    # ── Match management ─────────────────────────────────────────────── #

    def start_match(self) -> None:
        """Start (or restart) a game round.

        Calls game.start_new_game(), resets or creates GridTopLevel, and
        schedules the first AI move if the computer has the opening turn.
        """
        game = self._app.game
        game.start_new_game()

        if self._toplevel is None:
            # First match of the session — create the toplevel.
            from grid_toplevel import GridTopLevel   # deferred import
            self._toplevel = GridTopLevel(
                master=self,
                app=self._app,
                on_game_over=self._on_game_over,
            )
        else:
            # Rematch — reuse the existing toplevel.
            self._toplevel.reset()

        # Schedule AI's opening move if the computer goes first.
        if getattr(game.current_player, "is_ai", False):
            self.after(self._AI_DELAY_MS, self._do_ai_turn)

    def _do_ai_turn(self) -> None:
        """Delegate a single AI move to the GridTopLevel."""
        if self._toplevel is not None:
            self._toplevel.do_ai_turn()

    # ── Game-over callback ───────────────────────────────────────────── #

    def _on_game_over(self, result: str) -> None:
        """Called by GridTopLevel (via result modal) once the user dismisses it.

        Args:
            result: one of "p1_win", "p2_win", "draw", or "main_menu".
                    "main_menu" means the user chose to leave the session.
        """
        if result == "main_menu":
            self._exit_to_main_menu()
            return

        # Update counters.
        if result == "p1_win":
            self._session[self._app.p1_id]["wins"] += 1
        elif result == "p2_win":
            self._session[self._app.p2_id]["wins"] += 1
        elif result == "draw":
            self._session["draws"] += 1

        # Refresh the stats label NOW (after the modal is dismissed).
        self._refresh_stats_label()

        # Begin the next round.
        self.start_match()

    # ── Stats display ────────────────────────────────────────────────── #

    def _refresh_stats_label(self) -> None:
        """Rebuild the stats label text from current session counters."""
        p1  = self._app.p1_id
        p2  = self._app.p2_id
        text = (
            f"{p1}: {self._session[p1]['wins']}   "
            f"Draws: {self._session['draws']}   "
            f"{p2}: {self._session[p2]['wins']}"
        )
        self._stats_label.configure(text=text)

    # ── Navigation ───────────────────────────────────────────────────── #

    def _exit_to_main_menu(self) -> None:
        """Tear down the GridTopLevel and return to the main menu."""
        if self._toplevel is not None:
            self._toplevel.destroy()
            self._toplevel = None
        self._app.show_main_menu()