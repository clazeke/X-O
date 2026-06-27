"""
select_symbol_frame.py
----------------------
SelectSymbolFrame — Player 1 picks X or O; Player 2 receives the other.

Clicking a symbol writes the symbols to App then calls app.show_game(),
which is responsible for building Player/Game objects and navigating forward.
"""

from __future__ import annotations

import customtkinter as ctk


class SelectSymbolFrame(ctk.CTkFrame):
    """Symbol-selection screen.

    Layout (top-to-bottom, centred):
        ┌──────────────────────────────┐
        │     Choose your symbol       │
        │       [ X ]      [ O ]       │
        └──────────────────────────────┘

    Clicking either button:
        1. Writes app.p1_symbol / app.p2_symbol.
        2. Calls app.show_game() — App builds players/game and navigates.
    """

    _SYMBOL_BTN_SIZE  = 100
    _SYMBOL_FONT_SIZE = 40

    def __init__(self, parent, app) -> None:
        super().__init__(parent, fg_color="transparent")
        self._app = app
        self._build_ui()

    def _build_ui(self) -> None:
        self.columnconfigure(0, weight=1)
        row = 0

        ctk.CTkFrame(self, height=80, fg_color="transparent").grid(row=row, column=0)
        row += 1

        ctk.CTkLabel(
            self,
            text="Choose your symbol",
            font=ctk.CTkFont(family="Courier", size=26, weight="bold"),
        ).grid(row=row, column=0, pady=(0, 40))
        row += 1

        btn_row = ctk.CTkFrame(self, fg_color="transparent")
        btn_row.grid(row=row, column=0)

        for col, symbol in enumerate(("X", "O")):
            ctk.CTkButton(
                btn_row,
                text=symbol,
                font=ctk.CTkFont(
                    family="Courier",
                    size=self._SYMBOL_FONT_SIZE,
                    weight="bold",
                ),
                width=self._SYMBOL_BTN_SIZE,
                height=self._SYMBOL_BTN_SIZE,
                command=lambda s=symbol: self._on_symbol_chosen(s),
            ).grid(row=0, column=col, padx=20)
        row += 1

        ctk.CTkFrame(self, height=80, fg_color="transparent").grid(row=row, column=0)

    def _on_symbol_chosen(self, symbol: str) -> None:
        self._app.p1_symbol = symbol
        self._app.p2_symbol = "O" if symbol == "X" else "X"
        # App.show_game() builds players + game, then navigates.
        self._app.show_game()