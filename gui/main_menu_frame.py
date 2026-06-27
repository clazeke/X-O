"""
main_menu_frame.py
------------------
MainMenuFrame — the root screen of the GUI application.

Always exists for the lifetime of the program. Every other flow
returns here. Responsible only for rendering the menu and routing
the user to the correct next frame; all navigation state is written
to the App object before the frame transition happens.

Dependencies: customtkinter only — no game-logic imports needed here.
"""

import customtkinter as ctk


class MainMenuFrame(ctk.CTkFrame):
    """Root menu screen.

    Layout (top-to-bottom, centred):
        ┌─────────────────────────────┐
        │        Tic-Tac-Toe          │  ← title
        │   [ Player vs Player   ]    │
        │   [ Player vs Computer ]    │
        │   [     Leaderboard    ]    │
        │   [        Exit        ]    │
        └─────────────────────────────┘

    Constructor args:
        parent  — the CTk container this frame lives inside (root window)
        app     — the App controller; used for navigation and to set
                  app.mode before transitioning

    Navigation:
        "Player vs Player"   → sets app.mode = "pvp", calls app.show_select_id_p1()
        "Player vs Computer" → sets app.mode = "pvc", calls app.show_select_id_player()
        "Leaderboard"        → calls app.show_leaderboard()
        "Exit"               → calls app.show_exit()
    """

    _BTN_WIDTH  = 220
    _BTN_HEIGHT = 45

    def __init__(self, parent, app) -> None:
        super().__init__(parent, fg_color="transparent")
        self._app = app
        self._build_ui()

    # ── UI construction ──────────────────────────────────────────────── #

    def _build_ui(self) -> None:
        self.columnconfigure(0, weight=1)

        # ── Top spacer ────────────────────────────────────────────────── #
        ctk.CTkFrame(self, height=60, fg_color="transparent").grid(row=0, column=0)

        # ── Title ─────────────────────────────────────────────────────── #
        ctk.CTkLabel(
            self,
            text="Tic-Tac-Toe",
            font=ctk.CTkFont(family="Courier", size=36, weight="bold"),
        ).grid(row=1, column=0, pady=(0, 32))

        # ── Menu buttons ──────────────────────────────────────────────── #
        buttons = [
            ("Player vs Player",   self._on_pvp),
            ("Player vs Computer", self._on_pvc),
            ("Leaderboard",        self._on_leaderboard),
            ("Exit",               self._on_exit),
        ]

        for i, (label, command) in enumerate(buttons):
            ctk.CTkButton(
                self,
                text=label,
                font=ctk.CTkFont(family="Courier", size=14, weight="bold"),
                width=self._BTN_WIDTH,
                height=self._BTN_HEIGHT,
                command=command,
            ).grid(row=2 + i, column=0, pady=6)

        # ── Bottom spacer ─────────────────────────────────────────────── #
        ctk.CTkFrame(self, height=60, fg_color="transparent").grid(
            row=2 + len(buttons), column=0
        )

    # ── Button handlers ──────────────────────────────────────────────── #

    def _on_pvp(self) -> None:
        """Player vs Player selected."""
        self._app.mode = "pvp"
        self._app.show_select_id_p1()

    def _on_pvc(self) -> None:
        """Player vs Computer selected."""
        self._app.mode = "pvc"
        self._app.show_select_id_player()

    def _on_leaderboard(self) -> None:
        self._app.show_leaderboard()

    def _on_exit(self) -> None:
        self._app.show_exit()